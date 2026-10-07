import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return {"status": "World Model backend is running"}


@app.post("/ask")
def ask(data: Question):
    token = os.environ.get("HF_TOKEN")

    if not token:
        return {
            "answer": "HF_TOKEN is not configured."
        }

    response = requests.post(
        "https://router.huggingface.co/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-oss-120b:fastest",
            "messages": [
                {
                    "role": "user",
                    "content": data.question
                }
            ],
            "max_tokens": 300
        },
        timeout=60
    )

    if response.status_code != 200:
        return {
            "answer": "AI request failed: " + response.text
        }

    result = response.json()

    return {
        "answer": result["choices"][0]["message"]["content"]
    }
