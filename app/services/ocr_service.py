import base64
import requests
from pathlib import Path

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    OPENROUTER_MODEL,
    OCR_PROMPT
)


class OCRService:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.api_url = OPENROUTER_API_URL
        self.model = OPENROUTER_MODEL

    def extract_text(self, image_path: str) -> str:
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")

        with open(image_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}},
                    {"type": "text", "text": OCR_PROMPT}
                ]
            }],
            "max_tokens": 4096
        }

        response = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]
