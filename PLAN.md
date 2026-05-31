# 아파트 관리비 명세서 자동 분석 시스템

## 프로젝트 개요

아파트 관리비 고지서 이미지(JPG/HEIC)를 입력받아 자동으로 텍스트를 추출하고, 구조화된 데이터로 파싱하여 관리비 히스토리를 추적/분석하는 시스템 구축을 목표로 함.

## 연구 결과 요약

### 1단계: 이미지 → 텍스트 추출 (완료)
- **사용 모델**: `qwen/qwen3-vl-32b-instruct` (OpenRouter, 무료)
- **결과**: 관리비 명세서에서 정확한 텍스트 추출 성공
- **품질**: Markdown 표/헤딩으로 깔끔하게 정리됨

### 2단계: 텍스트 → 구조화 데이터 파싱 (완료)
- **사용 모델**: MiniMax API (OpenAI 호환)
- **결과**: JSON 형태의 구조화된 데이터 추출 성공
- **파싱 항목**: 기간, 총 부과액, 전기/난방/수도 사용량, 관리비 상세내역 등

### 테스트 데이터
- 이미지: `research-data/IMG_7070.jpg`
- 추출 텍스트: `research-data/output_qwen3-vl-32b-instruct.txt`
- 파싱 결과: `research-data/management_fee_parsed.md`

## 다음 단계 (미구현)

- [ ] 관리비 히스토리 저장소 (DB) 설계
- [ ] 배치 처리: 여러 명세서 이미지 일괄 처리
- [ ] 데이터베이스 기반 추세 분석/시각화
- [ ] CI/CD 파이프라인 (OpenRouter/MiniMax API 활용)
- [ ] CLI 또는 Web UI 개발

## 기술 스택 (예시)

| 단계 | 기술 |
|------|------|
| 이미지 → 텍스트 | OpenRouter + Qwen2-VL |
| 텍스트 → JSON | MiniMax API (또는 OpenRouter) |
| 저장소 | SQLite/PostgreSQL |
| UI | CLI / Streamlit / FastAPI |
