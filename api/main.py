from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import os
import httpx
import asyncio
import logging
import uuid
import time
from prometheus_client import Counter, Histogram, generate_latest

app = FastAPI()

# =============================
# Runtime configuration (ENV)
# =============================
RUNTIME_HOST = os.getenv("RUNTIME_HOST", "llm-runtime")
RUNTIME_PORT = os.getenv("RUNTIME_PORT", "11434")
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "15"))
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "2"))

BASE_URL = f"http://{RUNTIME_HOST}:{RUNTIME_PORT}"
GENERATE_URL = f"{BASE_URL}/api/generate"
TAGS_URL = f"{BASE_URL}/api/tags"


# =============================
# Logging configuration
# =============================
class RequestLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return msg, {"extra": {"request_id": self.extra.get("request_id", "-")}}


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(request_id)s] %(message)s",
)

logger = logging.getLogger(__name__)

# =============================
# Prometheus metrics
# =============================
REQUEST_COUNT = Counter("llm_requests_total", "Total number of LLM requests")

INFERENCE_TIME = Histogram(
    "llm_inference_seconds", "Time spent generating LLM response"
)

# =============================
# Concurrency limiter
# =============================
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "LLM API running"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")


async def get_active_model(client: httpx.AsyncClient):
    response = await client.get(TAGS_URL)
    response.raise_for_status()
    data = response.json()

    models = data.get("models", [])
    if not models:
        raise HTTPException(status_code=500, detail="No models available in runtime")

    return models[0]["name"]


@app.post("/generate")
async def generate(prompt: str):
    request_id = str(uuid.uuid4())[:8]
    log = RequestLoggerAdapter(logger, {"request_id": request_id})

    REQUEST_COUNT.inc()

    async with semaphore:
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                model_name = await get_active_model(client)

                log.info(
                    f"Incoming request | model={model_name} | prompt_len={len(prompt)}"
                )

                start_time = time.time()

                with INFERENCE_TIME.time():
                    response = await client.post(
                        GENERATE_URL,
                        json={
                            "model": model_name,
                            "prompt": prompt,
                            "stream": False,
                        },
                    )

                response.raise_for_status()

                duration = time.time() - start_time
                log.info(f"Inference completed in {duration:.3f}s")

                return response.json()

        except httpx.RequestError:
            log.error("Runtime unavailable")
            raise HTTPException(status_code=503, detail="LLM runtime unavailable")

        except httpx.HTTPStatusError as e:
            log.error(f"Runtime error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Runtime error: {str(e)}")
