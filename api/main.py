import os
import time
import uuid
import logging
import asyncio
import httpx

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# =============================
# Configuration
# =============================

BASE_URL = os.getenv("LLM_RUNTIME_URL", "http://llm-runtime:11434")
TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
MAX_CONCURRENT_REQUESTS = int(os.getenv("LLM_MAX_CONCURRENCY", "2"))

# =============================
# Logging Setup
# =============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

# =============================
# Prometheus Metrics
# =============================

LLM_REQUESTS = Counter("llm_requests_total", "Total number of LLM requests")

LLM_REQUEST_ERRORS = Counter(
    "llm_request_errors_total", "Total number of failed LLM requests"
)

LLM_INFERENCE_SECONDS = Histogram(
    "llm_inference_seconds", "Time spent generating LLM response"
)

LLM_INFLIGHT = Gauge("llm_requests_inflight", "Number of in-flight LLM requests")

# =============================
# App & Concurrency
# =============================

app = FastAPI()
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

# =============================
# Helpers
# =============================


async def get_active_model(client: httpx.AsyncClient) -> str:
    response = await client.get(f"{BASE_URL}/api/tags")
    response.raise_for_status()
    data = response.json()

    models = data.get("models", [])
    if not models:
        raise HTTPException(
            status_code=500, detail="No models available in LLM runtime"
        )

    return models[0]["name"]


# =============================
# Endpoints
# =============================


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/generate")
async def generate(prompt: str):
    request_id = uuid.uuid4().hex[:8]
    start_time = time.time()

    async with semaphore:
        LLM_INFLIGHT.inc()
        LLM_REQUESTS.inc()

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                model_name = await get_active_model(client)

                logger.info(
                    f"[{request_id}] Incoming request | model={model_name} | prompt_len={len(prompt)}"
                )

                response = await client.post(
                    f"{BASE_URL}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": prompt,
                        "stream": False,
                    },
                )

                response.raise_for_status()
                data = response.json()

                duration = time.time() - start_time
                LLM_INFERENCE_SECONDS.observe(duration)

                logger.info(f"[{request_id}] Inference completed in {duration:.3f}s")

                return data

        except Exception as e:
            LLM_REQUEST_ERRORS.inc()
            logger.exception(f"[{request_id}] Request failed: {e}")
            raise HTTPException(status_code=500, detail="LLM runtime unavailable")

        finally:
            LLM_INFLIGHT.dec()
