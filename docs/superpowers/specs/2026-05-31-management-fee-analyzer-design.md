# 아파트 관리비 명세서 분석 시스템 설계

## 1. 개요

아파트 관리비 고지서 이미지(JPG/HEIC)를 입력받아 자동으로 텍스트를 추출하고, 구조화된 데이터로 파싱하여 관리비 히스토리를 추적/분석하는 시스템.

**사용자**: 개인/가정용 (단일 사용자)
**실행 환경**: Kubernetes 서버 (Docker 컨테이너)

---

## 2. 기술 스택

| 구성 요소 | 기술 |
|----------|------|
| UI 프레임워크 | Streamlit |
| 로컬 스토리지 | SQLite |
| 이미지 → 텍스트 | OpenRouter + `qwen/qwen3-vl-32b-instruct` |
| 텍스트 → JSON | MiniMax API |
| 시각화 | Streamlit + Plotly |
| 배포 | Docker 컨테이너 (Kubernetes 호환) |

---

## 3. 프로젝트 구조

```
app/
├── main.py              # Streamlit 진입점
├── config.py            # 설정 (DB 경로, API 설정)
├── database.py          # SQLite CRUD
├── services/
│   ├── __init__.py
│   ├── ocr_service.py   # OpenRouter API (이미지→텍스트)
│   └── parser_service.py # MiniMax API (텍스트→JSON)
├── pages/
│   ├── 1_上传.py        # 이미지 업로드/처리
│   ├── 2_历史.py         # 처리 기록 조회
│   ├── 3_趋势.py         # 추이 차트
│   └── 4_设置.py         # API 설정
└── requirements.txt
```

---

## 4. 데이터베이스 스키마

### management_fees 테이블 (월별 관리비 요약)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 고유 ID |
| date | TEXT | 고지서 월 (YYYY-MM) |
| total_amount | INTEGER | 총 부과액 (원) |
| electricity_kwh | REAL | 전기 사용량 (kWh) |
| electricity_amount | INTEGER | 전기 요금 (원) |
| gas_kg | REAL | 가스 사용량 (kg) |
| gas_amount | INTEGER | 가스 요금 (원) |
| water_cbm | REAL | 수도 사용량 (m³) |
| water_amount | INTEGER | 수도 요금 (원) |
| heating_kwh | REAL | 난방 열에너지 (kWh) |
| heating_amount | INTEGER | 난방비 (원) |
| created_at | TEXT | 생성 시각 |

### raw_data 테이블 (원본 데이터 보관)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 고유 ID |
| fee_id | INTEGER FK | management_fees.id 참조 |
| image_path | TEXT | 원본 이미지 경로 |
| extracted_text | TEXT | OCR 추출 텍스트 |
| parsed_json | TEXT | 원본 파싱 결과 (JSON 문자열) |
| model_used | TEXT | 사용한 VLM 모델명 |
| created_at | TEXT | 생성 시각 |

---

## 5. 페이지별 기능

### 5.1 업로드 페이지 (1_上传.py)

**기능:**
- 이미지 파일 업로드 (JPG, HEIC, PNG 지원)
- 단일/배치 업로드 가능
- 업로드 후 OCR + 파싱 자동 실행
- 파싱 결과 표시 (표 형식)
- 저장 전 확인/수정 가능
- 오류 시 원본 텍스트와 재시도 옵션

**처리 과정:**
1. 이미지 base64 인코딩
2. OpenRouter API 호출 → 텍스트 추출
3. 추출된 텍스트 → MiniMax API → JSON 파싱
4. 결과 사용자에게 표시
5. 저장确认

### 5.2 이력 페이지 (2_历史.py)

**기능:**
- 저장된 관리비 목록 표시 (테이블)
- 월별/날짜순 정렬
- 상세 보기: 파싱된 데이터 + 원본 이미지
- 삭제 기능
- 필터: 날짜 범위

### 5.3 추이 페이지 (3_趋势.py)

**기능:**
- 월별 총액 라인 차트
- 전기/가스/수도/난방 별도 차트
- 기간 선택 (전체/최근 6개월/최근 1년)
- Plotly 기반インタラクティブ图表

### 5.4 설정 페이지 (4_设置.py)

**기능:**
- API 키 표시 (마스킹)
- 현재 설정값 확인
- 저장소 경로 확인
- 테스트 버튼: API 연결 테스트

---

## 6. 서비스 레이어

### 6.1 ocr_service.py

```python
class OCRService:
    def extract_text(image_path: str) -> str:
        """OpenRouter API로 이미지에서 텍스트 추출"""
        # base64 인코딩 → OpenRouter → 응답 파싱
```

**사용 모델**: `qwen/qwen3-vl-32b-instruct`
**프롬프트**: "이 이미지에서 텍스트를 모두 추출해주세요."

### 6.2 parser_service.py

```python
class ParserService:
    def parse_to_json(extracted_text: str) -> dict:
        """MiniMax API로 텍스트를 구조화된 JSON으로 변환"""
        # JSONスキーマ指定 → 파싱 → 검증
```

**파싱 대상 필드**: date, total_amount, electricity_*, gas_*, water_*, heating_*

---

## 7. 배포

### Docker (Dockerfile)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Kubernetes

- Deployment: 단일 Pod (个人用)
- Service: ClusterIP 또는 LoadBalancer
- PersistentVolumeClaim: SQLite 파일 저장을 위한 볼륨

---

## 8. 오류 처리

| 상황 | 처리 |
|------|------|
| OCR 실패 | 오류 메시지 + 재시도 버튼 |
| 파싱 실패 | 원본 텍스트 표시 + 수동 입력 옵션 |
| API 키 오류 | 설정 페이지로 리다이렉트 |
| 이미지 형식不支持 | 지원 형식 안내 메시지 |
| DB 오류 | 로그 기록 + 사용자에게 알림 |

---

## 9. 구현 순서

1. **기반 설정**: requirements.txt, config.py, database.py
2. **서비스 레이어**: ocr_service.py, parser_service.py
3. **UI 페이지**: 1_上传 → 2_历史 → 3_趋势 → 4_设置
4. **Dockerfile**: 컨테이너화
5. **테스트 및 검증**

---

## 10. 참고 자료

- RESEARCH.md: API 테스트 결과 및 모델 비교
- research-data/: 테스트 이미지 및 파싱 결과 샘플
