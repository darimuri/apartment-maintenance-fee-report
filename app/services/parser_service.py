import json
import logging
import re
import requests

logger = logging.getLogger(__name__)

from app.config import (
    MINIMAX_API_KEY,
    MINIMAX_API_URL,
    MINIMAX_MODEL
)


class ParserService:
    def __init__(self):
        self.api_key = MINIMAX_API_KEY
        self.api_url = MINIMAX_API_URL
        self.model = MINIMAX_MODEL

    def parse_to_json(self, extracted_text: str) -> dict:
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY is not set")

        logger.info("Starting JSON parsing, input text length: %d", len(extracted_text))

        prompt = f"""다음 관리비 명세서 텍스트를 JSON으로 변환해주세요.
JSON 스키마:
{{
  "date": "YYYY년 MM월분",
  "total_amount": 정수 (원),
  "address": {{"building": "동", "unit": "호", "area": 면적}},
  "payment_deadline": "날짜",
  "previous_year_comparison": {{
    "electricity": {{"previous_month_reading": 정수, "current_month_reading": 정수, "current_month_usage": 실수, "previous_month_usage": 실수, "previous_year_usage": 실수}},
    "hot_water": {{...}},
    "water": {{...}},
    "heating": {{...}}
  }},
  "energy_usage_comparison": {{"my_usage_kwh": 정수, "same_area_avg_kwh": 정수, "comparison_percent": 정수}},
  "electricity_breakdown": {{"total": 정수, "same_area_avg": 정수, "power_rate": 정수, "climate_env": 정수, "fuel_adjust": 정수, "elevator_electric": 정수, "common_electric": 정수}},
  "heating_breakdown": {{"total": 정수, "same_area_avg": 정수, "basic_heating": 정수, "common_heating": 정수, "hot_water_usage": 정수}},
  "management_fee_details": {{항목별 금액}},
  "utility_charges": {{항목별 금액}},
  "payment_info": {{"autopay": 불리언, "bank": 문자열, "apt_code": 문자열}},
  "contact": {{"management_office": 문자열}}
}}

텍스트:
{extracted_text}

JSON만 반환하세요."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2048
        }

        logger.debug("Calling MiniMax API: %s", self.api_url)

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            logger.info("MiniMax response status: %s", response.status_code)

            if not response.ok:
                key_preview = self.api_key[:8] + "..." if len(self.api_key) > 8 else "***"
                logger.error("MiniMax API error: %s %s (key: %s)", response.status_code, response.text, key_preview)
                response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            logger.info("JSON parsing completed, output length: %d", len(content))

            # Remove thinking tags if present (MiniMax reasoning content)
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)

            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            return json.loads(content)

        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error during parsing: %s", e)
            raise
        except requests.exceptions.RequestException as e:
            logger.error("Request error during parsing: %s", e)
            raise