# 아파트 관리비 명세서 분석 시스템 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Streamlit 앱으로 관리비 고지서 이미지 처리 → 텍스트 추출 → JSON 파싱 → SQLite 저장 → 추이 시각화

**Architecture:** Streamlit 단일 앱 + SQLite 로컬 저장 + OpenRouter OCR + MiniMax 파싱

**Tech Stack:** Python 3.11, Streamlit, SQLite, OpenRouter API, MiniMax API, Plotly

---

## 파일 구조

```
app/
├── main.py              # Streamlit 진입점
├── config.py            # DB/API 설정
├── database.py          # SQLite CRUD
├── services/
│   ├── __init__.py
│   ├── ocr_service.py   # OpenRouter (이미지→텍스트)
│   └── parser_service.py # MiniMax (텍스트→JSON)
├── pages/
│   ├── 1_上传.py        # 이미지 업로드
│   ├── 2_历史.py         # 처리 기록
│   ├── 3_趋势.py         # 추이 차트
│   └── 4_设置.py         # 설정
└── requirements.txt

Dockerfile
```

---

## Phase 1: 기반 설정

### Task 1: requirements.txt

**Files:**
- Create: `app/requirements.txt`

- [ ] **Step 1: requirements.txt 작성**

```
streamlit>=1.28
plotly>=5.18
requests>=2.31
python-dotenv>=1.0
pillow>=10.0
```

- [ ] **Step 2: 커밋**

```bash
git add app/requirements.txt && git commit -m "chore: add requirements.txt"
```

---

### Task 2: config.py

**Files:**
- Create: `app/config.py`

- [ ] **Step 1: config.py 작성**

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = str(DATA_DIR / "management_fees.db")
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = "qwen/qwen3-vl-32b-instruct"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

MINIMAX_API_KEY = os.getenv("OPENAI_API_KEY", "")
MINIMAX_API_URL = os.getenv("OPENAI_BASE_URL", "https://api.minimax.io/v1")
MINIMAX_MODEL = os.getenv("OPENAI_MODEL", "MiniMax-M2.7")

OCR_PROMPT = "이 이미지에서 텍스트를 모두 추출해주세요."
```

- [ ] **Step 2: app/__init__.py 작성**

```python
```

- [ ] **Step 3: app/services/__init__.py 작성**

```python
```

- [ ] **Step 4: 커밋**

```bash
git add app/config.py app/__init__.py app/services/__init__.py && git commit -m "feat: add config.py with settings"
```

---

### Task 3: database.py

**Files:**
- Create: `app/database.py`

- [ ] **Step 1: database.py 작성**

```python
import sqlite3
import json
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

from app.config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


@contextmanager
def get_cursor():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS management_fees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_amount INTEGER,
                address_building TEXT,
                address_unit TEXT,
                address_area REAL,
                payment_deadline TEXT,
                electricity_kwh REAL,
                electricity_amount INTEGER,
                gas_kg REAL,
                gas_amount INTEGER,
                water_cbm REAL,
                water_amount INTEGER,
                heating_kwh REAL,
                heating_amount INTEGER,
                management_fee_details TEXT,
                utility_charges TEXT,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fee_id INTEGER,
                image_path TEXT,
                extracted_text TEXT,
                parsed_json TEXT,
                model_used TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (fee_id) REFERENCES management_fees(id)
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fees_date ON management_fees(date)
        """)


def insert_fee(fee_data: dict, raw_data: dict) -> int:
    init_db()
    now = datetime.now().isoformat()

    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO management_fees (
                date, total_amount, address_building, address_unit, address_area,
                payment_deadline, electricity_kwh, electricity_amount,
                gas_kg, gas_amount, water_cbm, water_amount,
                heating_kwh, heating_amount, management_fee_details, utility_charges, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fee_data.get("date"),
            fee_data.get("total_amount"),
            fee_data.get("address", {}).get("building"),
            fee_data.get("address", {}).get("unit"),
            fee_data.get("address", {}).get("area"),
            fee_data.get("payment_deadline"),
            fee_data.get("previous_year_comparison", {}).get("electricity", {}).get("current_month_usage"),
            fee_data.get("electricity_breakdown", {}).get("total"),
            fee_data.get("previous_year_comparison", {}).get("hot_water", {}).get("current_month_usage"),
            fee_data.get("heating_breakdown", {}).get("hot_water_usage"),
            fee_data.get("previous_year_comparison", {}).get("water", {}).get("current_month_usage"),
            fee_data.get("utility_charges", {}).get("household_water"),
            fee_data.get("previous_year_comparison", {}).get("heating", {}).get("current_month_usage"),
            fee_data.get("heating_breakdown", {}).get("total"),
            json.dumps(fee_data.get("management_fee_details", {})),
            json.dumps(fee_data.get("utility_charges", {})),
            now
        ))
        fee_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO raw_data (
                fee_id, image_path, extracted_text, parsed_json, model_used, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            fee_id,
            raw_data.get("image_path"),
            raw_data.get("extracted_text"),
            json.dumps(fee_data),
            raw_data.get("model_used"),
            now
        ))

        return fee_id


def get_all_fees():
    init_db()
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT id, date, total_amount, address_building, address_unit,
                   electricity_kwh, electricity_amount, gas_kg, gas_amount,
                   water_cbm, water_amount, heating_kwh, heating_amount, created_at
            FROM management_fees ORDER BY date DESC
        """)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_fee_by_id(fee_id: int) -> Optional[dict]:
    init_db()
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM management_fees WHERE id = ?", (fee_id,))
        row = cursor.fetchone()
        if not row:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))


def get_raw_data_by_fee_id(fee_id: int) -> Optional[dict]:
    init_db()
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM raw_data WHERE fee_id = ?", (fee_id,))
        row = cursor.fetchone()
        if not row:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))


def delete_fee(fee_id: int):
    init_db()
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM raw_data WHERE fee_id = ?", (fee_id,))
        cursor.execute("DELETE FROM management_fees WHERE id = ?", (fee_id,))
```

- [ ] **Step 2: 커밋**

```bash
git add app/database.py && git commit -m "feat: add database.py with SQLite CRUD"
```

---

## Phase 2: 서비스 레이어

### Task 4: ocr_service.py

**Files:**
- Create: `app/services/ocr_service.py`

- [ ] **Step 1: ocr_service.py 작성**

```python
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
```

- [ ] **Step 2: 커밋**

```bash
git add app/services/ocr_service.py && git commit -m "feat: add OCR service with OpenRouter"
```

---

### Task 5: parser_service.py

**Files:**
- Create: `app/services/parser_service.py`

- [ ] **Step 1: parser_service.py 작성**

```python
import json
import requests

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

        response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        return json.loads(content)
```

- [ ] **Step 2: 커밋**

```bash
git add app/services/parser_service.py && git commit -m "feat: add Parser service with MiniMax"
```

---

## Phase 3: UI 페이지

### Task 6: main.py

**Files:**
- Create: `app/main.py`

- [ ] **Step 1: main.py 작성**

```python
import streamlit as st
from app.database import init_db

st.set_page_config(
    page_title="아파트 관리비 분석",
    page_icon="📊",
    layout="wide"
)

init_db()

st.title("📊 아파트 관리비 명세서 분석")
st.sidebar.success("메뉴를 선택하세요")
```

- [ ] **Step 2: 커밋**

```bash
git add app/main.py && git commit -m "feat: add Streamlit main entry point"
```

---

### Task 7: 1_上传.py (이미지 업로드)

**Files:**
- Create: `app/pages/1_上传.py`

- [ ] **Step 1: 1_上传.py 작성**

```python
import streamlit as st
import shutil
from pathlib import Path
from datetime import datetime

from app.config import UPLOAD_DIR, OPENROUTER_MODEL
from app.database import insert_fee
from app.services.ocr_service import OCRService
from app.services.parser_service import ParserService


st.header("📤 이미지 업로드 및 처리")

uploaded_files = st.file_uploader(
    "관리비 고지서 이미지 파일을 선택하세요 (JPG, HEIC, PNG)",
    type=["jpg", "jpeg", "heic", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"선택된 파일: {len(uploaded_files)}개")

    if "processing" not in st.session_state:
        st.session_state.processing = False

    if st.button("🚀 처리 시작", disabled=st.session_state.processing):
        st.session_state.processing = True
        results = []

        for uploaded_file in uploaded_files:
            with st.spinner(f"'{uploaded_file.name}' 처리 중..."):
                try:
                    save_path = UPLOAD_DIR / uploaded_file.name
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    ocr = OCRService()
                    extracted_text = ocr.extract_text(str(save_path))

                    parser = ParserService()
                    parsed_data = parser.parse_to_json(extracted_text)

                    raw_data = {
                        "image_path": str(save_path),
                        "extracted_text": extracted_text,
                        "model_used": OPENROUTER_MODEL
                    }

                    fee_id = insert_fee(parsed_data, raw_data)

                    results.append({
                        "file": uploaded_file.name,
                        "status": "✅ 성공",
                        "fee_id": fee_id,
                        "date": parsed_data.get("date"),
                        "total": parsed_data.get("total_amount")
                    })

                except Exception as e:
                    results.append({
                        "file": uploaded_file.name,
                        "status": f"❌ 실패: {str(e)}",
                        "fee_id": None,
                        "date": None,
                        "total": None
                    })

        st.session_state.processing = False

        st.subheader("📋 처리 결과")
        for r in results:
            st.write(f"- {r['file']}: {r['status']}")
            if r["fee_id"]:
                st.write(f"  - 기간: {r['date']}, 총액: {r['total']:,}원")

        if any(r["fee_id"] for r in results):
            st.success("처리가 완료되었습니다!")
```

- [ ] **Step 2: 커밋**

```bash
git add app/pages/1_上传.py && git commit -m "feat: add upload page"
```

---

### Task 8: 2_历史.py (이력)

**Files:**
- Create: `app/pages/2_历史.py`

- [ ] **Step 1: 2_历史.py 작성**

```python
import streamlite as st
import json

from app.database import get_all_fees, get_fee_by_id, get_raw_data_by_fee_id, delete_fee


st.header("📋 처리 기록")

fees = get_all_fees()

if not fees:
    st.info("저장된 관리비 내역이 없습니다.")
else:
    st.write(f"총 {len(fees)}건")

    for fee in fees:
        with st.expander(f"{fee['date']} - {fee['total_amount']:,}원"):
            st.write(f"**동/호:** {fee['address_building']} {fee['address_unit']}")
            st.write(f"**전기:** {fee['electricity_kwh']} kWh ({fee['electricity_amount']:,}원)")
            st.write(f"**수도:** {fee['water_cbm']} m³ ({fee['water_amount']:,}원)")
            st.write(f"**난방:** {fee['heating_kwh']} ({fee['heating_amount']:,}원)")
            st.write(f"**생성일:** {fee['created_at'][:10]}")

            if st.button(f"삭제", key=f"delete_{fee['id']}"):
                delete_fee(fee['id'])
                st.rerun()
```

- [ ] **Step 2: 커밋**

```bash
git add app/pages/2_历史.py && git commit -m "feat: add history page"
```

---

### Task 9: 3_趋势.py (추이)

**Files:**
- Create: `app/pages/3_趋势.py`

- [ ] **Step 1: 3_趋势.py 작성**

```python
import streamlit as st
import plotly.express as px

from app.database import get_all_fees


st.header("📈 관리비 추이")

fees = get_all_fees()

if not fees:
    st.info("표시할 데이터가 없습니다.")
else:
    df = pd.DataFrame(fees)
    df = df.sort_values("date")

    period = st.selectbox(
        "기간 선택",
        ["전체", "최근 6개월", "최근 1년"]
    )

    if period == "최근 6개월":
        df = df.tail(6)
    elif period == "최근 1년":
        df = df.tail(12)

    st.subheader("월별 총액")
    fig = px.line(
        df,
        x="date",
        y="total_amount",
        markers=True,
        labels={"date": "월", "total_amount": "총액 (원)"}
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("전기 사용량 & 요금")
        fig2 = px.bar(
            df,
            x="date",
            y=["electricity_kwh", "electricity_amount"],
            labels={"value": "값", "variable": "항목"}
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("수도 사용량 & 요금")
        fig3 = px.bar(
            df,
            x="date",
            y=["water_cbm", "water_amount"],
            labels={"value": "값", "variable": "항목"}
        )
        st.plotly_chart(fig3, use_container_width=True)
```

- [ ] **Step 2: import pandas as pd 추가 확인**

```python
import pandas as pd
```

- [ ] **Step 3: 커밋**

```bash
git add app/pages/3_趋势.py && git commit -m "feat: add trends page with Plotly charts"
```

---

### Task 10: 4_设置.py (설정)

**Files:**
- Create: `app/pages/4_设置.py`

- [ ] **Step 1: 4_设置.py 작성**

```python
import streamlit as st

from app.config import (
    DB_PATH, UPLOAD_DIR,
    OPENROUTER_API_KEY, OPENROUTER_MODEL,
    MINIMAX_API_KEY, MINIMAX_API_URL, MINIMAX_MODEL
)


st.header("⚙️ 설정")

st.subheader("API 설정")

st.write(f"**OpenRouter 모델:** `{OPENROUTER_MODEL}`")
if OPENROUTER_API_KEY:
    masked = OPENROUTER_API_KEY[:8] + "..." + OPENROUTER_API_KEY[-4:]
    st.write(f"**OpenRouter API Key:** `{masked}`")
else:
    st.warning("OPENROUTER_API_KEY가 설정되지 않았습니다")

st.write(f"**MiniMax API URL:** `{MINIMAX_API_URL}`")
st.write(f"**MiniMax 모델:** `{MINIMAX_MODEL}`")
if MINIMAX_API_KEY:
    masked = MINIMAX_API_KEY[:8] + "..." + MINIMAX_API_KEY[-4:]
    st.write(f"**MiniMax API Key:** `{masked}`")
else:
    st.warning("MINIMAX_API_KEY가 설정되지 않았습니다")

st.subheader("저장소")
st.write(f"**DB 경로:** `{DB_PATH}`")
st.write(f"**업로드 경로:** `{UPLOAD_DIR}`")
```

- [ ] **Step 2: 커밋**

```bash
git add app/pages/4_设置.py && git commit -m "feat: add settings page"
```

---

## Phase 4: Docker

### Task 11: Dockerfile

**Files:**
- Create: `Dockerfile`

- [ ] **Step 1: Dockerfile 작성**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY .env .

ENV PYTHONPATH=/app

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

- [ ] **Step 2: .dockerignore 작성**

```
.env
.git
.gitignore
README.md
research-data/
docs/
.claude/
*.md
```

- [ ] **Step 3: 커밋**

```bash
git add Dockerfile .dockerignore && git commit -m "feat: add Dockerfile for containerization"
```

---

## Phase 5: 검증

### Task 12: 앱 실행 검증

- [ ] **Step 1: 의존성 설치**

```bash
pip install -r app/requirements.txt
```

- [ ] **Step 2: 앱 실행 테스트**

```bash
streamlit run app/main.py
```

- [ ] **Step 3: 브라우저에서 수동 검증**
- 업로드 페이지에서 테스트 이미지 처리
- 이력 페이지에서 저장된 데이터 확인
- 추이 페이지에서 차트 표시 확인

---

## 구현 순서 (Summary)

1. Task 1: requirements.txt
2. Task 2: config.py + __init__.py
3. Task 3: database.py
4. Task 4: ocr_service.py
5. Task 5: parser_service.py
6. Task 6: main.py
7. Task 7: 1_上传.py
8. Task 8: 2_历史.py
9. Task 9: 3_趋势.py
10. Task 10: 4_设置.py
11. Task 11: Dockerfile
12. Task 12: 검증
