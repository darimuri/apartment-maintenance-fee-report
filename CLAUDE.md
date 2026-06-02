# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

아파트 관리비 고지서 이미지를 분석하여 SQLite DB에 저장하고 추이를 시각화하는 Streamlit 앱.

## 개발 명령어

```bash
# 앱 실행
PYTHONPATH=. streamlit run app/main.py

# 테스트 실행 (전체)
python -m pytest tests/ -v

# 테스트 실행 (단일 파일)
python -m pytest tests/test_database.py -v

# 테스트 실행 (단일 테스트)
python -m pytest tests/test_database.py::TestDatabaseSchema::test_init_db_creates_tables -v
```

## 기술 스택

- **UI**: Streamlit 1.28+ (`st.navigation` 사용, 한국어 메뉴)
- **DB**: SQLite (테스트 시 `TEST_DB_PATH` 환경변수 사용)
- **이미지→텍스트**: OpenRouter + `qwen/qwen3-vl-32b-instruct`
- **텍스트→JSON**: MiniMax API (OpenAI 호환)
- **시각화**: Plotly

## 아키텍처

```
app/
├── main.py          # Streamlit 진입점, 네비게이션 설정
├── config.py        # DB 경로, API 키, 환경변수 로드
├── database.py      # SQLite CRUD (management_fees + raw_data 테이블)
├── services/
│   ├── ocr_service.py    # OpenRouter: 이미지→텍스트
│   └── parser_service.py  # MiniMax: 텍스트→JSON
└── pages/
    ├── 1_Upload.py    # 이미지 업로드 + OCR + 파싱 + 저장
    ├── 2_History.py   # 저장된 관리비 목록 (None 처리 완료)
    ├── 3_Trends.py    # Plotly 추이 차트 (None/dtype 처리 완료)
    └── 4_Settings.py  # 설정 페이지

data/
├── management_fees.db  # SQLite DB
└── uploads/           # 업로드된 이미지
```

## DB 스키마

**management_fees**: date, total_amount, address_*, electricity_*, gas_*, water_*, heating_*, management_fee_details(JSON), utility_charges(JSON)

**raw_data**: fee_id(FK), image_path, extracted_text, parsed_json(JSON), model_used, created_at

## 환경변수

`.env` 파일 사용:
- `OPENROUTER_API_KEY` - 이미지→텍스트
- `OPENAI_API_KEY` / `MINIMAX_API_KEY` - 텍스트→JSON
- `TEST_DB_PATH` - 테스트용 별도 DB 경로