from fastapi import FastAPI, HTTPException
import os
import httpx
import asyncio
import logging
import uuid
import time

# ================================
# Logging (SafeFormatter)
# ================================


class SafeFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return super().format(record)


handler = logging.StreamHandler()
formatter = SafeFormatter("%(asctime)s [%(levelname)s] [%(request_id)s] %(message)s")
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers = [handler]

# Wyciszamy httpx debug
logging.getLogger("httpx").setLevel(logging.WARNING)

# ================================
# Config z ENV
# ================================

RUNTIME_HOST = os.getenv("RUNTIME_HOST", "llm-runtime")
RUNTIME_PORT = os.getenv("RUNTIME_PORT", "11434")

TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "15"))
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "2"))

BASE_URL = f"http://{RUNTIME_HOST}:{RUNTIME_PORT}"

# Rate limiter
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

app = FastAPI()


# ================================
# Health endpoints
# ================================


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "LLM API running"}


# ================================
# Runtime helpers
# ================================


async def get_active_model(client: httpx.AsyncClient) -> str:
    response = await client.get(f"{BASE_URL}/api/tags")
    response.raise_for_status()

    data = response.json()
    models = data.get("models", [])

    if not models:
        raise HTTPException(status_code=503, detail="No model loaded in runtime")

    return models[0]["name"]


# ================================
# Generate endpoint
# ================================


@app.post("/generate")
async def generate(prompt: str):

    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    async with semaphore:
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:

                # 🔥 Pobieramy model dynamicznie
                model_name = await get_active_model(client)

                logger.info(
                    f"Incoming request | model={model_name} | prompt_len={len(prompt)}",
                    extra={"request_id": request_id},
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

            duration = time.time() - start_time

            logger.info(
                f"Inference completed in {duration:.3f}s",
                extra={"request_id": request_id},
            )

            return response.json()

        except httpx.RequestError:
            logger.error(
                "LLM runtime unavailable",
                extra={"request_id": request_id},
            )
            raise HTTPException(status_code=503, detail="LLM runtime unavailable")

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Runtime HTTP error: {str(e)}",
                extra={"request_id": request_id},
            )
            raise HTTPException(status_code=500, detail=f"Runtime error: {str(e)}")
