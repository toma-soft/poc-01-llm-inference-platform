from fastapi import FastAPI
import os
import requests

app = FastAPI()

MODEL_NAME = os.getenv("MODEL_NAME", "tinyllama")
OLLAMA_URL = "http://ollama:11434/api/generate"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": f"LLM Platform running. Model: {MODEL_NAME}"}

@app.post("/generate")
def generate(prompt: str):
    response = requests.post(
        OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False}
    )
    return response.json()
