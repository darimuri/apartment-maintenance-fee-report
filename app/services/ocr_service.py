import base64
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

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

        logger.info("Starting OCR extraction: %s", image_path)

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

        logger.debug("Calling OpenRouter API: %s", self.api_url)

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
            logger.info("OpenRouter response status: %s", response.status_code)

            if not response.ok:
                key_preview = self.api_key[:8] + "..." + self.api_key[-4:] if len(self.api_key) > 12 else "***"
                logger.error("OpenRouter API error: %s %s (key: %s)", response.status_code, response.text, key_preview)
                response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            logger.info("OCR extraction completed, text length: %d", len(content))
            return content

        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error during OCR: %s", e)
            raise
        except requests.exceptions.RequestException as e:
            logger.error("Request error during OCR: %s", e)
            raise
