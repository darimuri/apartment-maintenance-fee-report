# IMG_7070 이미지 텍스트 추출 연구

## 작업 내용

1. **HEIC → JPG 변환**: `convert IMG_7070.heic IMG_7070.jpg`로 성공 (3.7MB)
2. **OCR 시도**: Tesseract OCR 미설치로 실패
3. **LLM 기반 OCR 탐색**: 여러 API 조사

## 조사된 LLM 옵션

### Claude API (불가 - 사용자 거부)
- Vision 모델 (`claude-opus-4-7`)으로 이미지 텍스트 추출 가능
- base64 인코딩된 이미지와 메시지 API 호출
- 코드 구현 완료였으나 사용자가 거부

### MiniMax API (없음)
- 이미지 생성, 영상 생성, 음성 합성 특화
- **이미지 이해/OCR 텍스트 추출 API 미제공**

### Ollama (로컬)
- `llava`, `bakllava` 등 multimodal 모델 지원
- 로컬에서 실행 가능
- 이미지 텍스트 추출 기능 있음

### OpenRouter (API)
- Claude, Gemini, GPT-4 Vision 등 다양한 비전 모델 제공
- API 키로 바로 사용 가능

## Hugging Face Inference Providers 테스트 결과

### 테스트 내용
- **텍스트 전용 chat completion**: ✅ 성공
  - 모델: `Qwen/Qwen2.5-7B-Instruct`
  - 결과: 정상적으로 응답 반환
- **Vision Language Model (VLM)**: ❌ 실패
  - 테스트 모델: `HuggingFaceM4/idefics2-8b`, `meta-llama/Llama-3.2-11B-Vision-Instruct`, `Qwen/Qwen3-VL-235B-A22B-Instruct`
  - 에러: `"The requested model 'xxx' is not a chat model."`
  - 사용 가능한 Vision 모델: 58개 중 3개 (모두 200B+ 파라미터로 실용성 없음)

### 결론
- Hugging Face Inference Providers 서버리스 API는 **텍스트 전용 LLM만 지원**
- Vision 모델은 지원하지 않음 (서버리스 환경의限制)
- 문서의 VLM 예제는 **로컬 TGI 서버**나 **Inference Endpoints** 기준임

## 무료 클라우드 Vision API (조사중)

### Hugging Face Inference Providers
- **무료 tier**: 일일 요청 수 제한
- **VLM 지원**: ❌ 서버리스 API에서는 Vision 모델 미지원
- **텍스트 LLM**: ✅ 정상 작동
- **대안**: 로컬 TGI 또는 Inference Endpoints 필요

### Deepinfra
- 무료 tier 있음
- VLM 지원 가능성 있음 (調査 필요)

### Lambda Labs
- 무료 tier 있음
- LlamaVision, Qwen2VL 등 지원

### Replicate
- 무료 크레딧 있음
- Vision 모델 호스팅

### OpenRouter ✅ 테스트 성공
- **환경변수**: `OPENROUTER_API_KEY` 필요
- **테스트 결과 비교**:

| 모델 | 결과 품질 | 크기 | 비고 | 응답 파일 |
|------|-----------|------|------|-----------|
| `meta-llama/llama-3.2-11b-vision-instruct` | ❌ | 11,250 chars | gibberish 90%+, 실제로 사용 불가 | [output_llama-3.2-11b-vision-instruct.txt](research-data/output_llama-3.2-11b-vision-instruct.txt) |
| `qwen/qwen3-vl-8b-instruct` | ✅ 양호 | 1,966 chars | Plain text, 핵심 정보 정확하나 누락 있음 | [output_qwen3-vl-8b-instruct.txt](research-data/output_qwen3-vl-8b-instruct.txt) |
| `qwen/qwen3-vl-32b-instruct` | ✅✅ **최고** | 3,062 chars | Markdown 표/헤딩으로 깔끔 정리, 정보 완전 | [output_qwen3-vl-32b-instruct.txt](research-data/output_qwen3-vl-32b-instruct.txt) |
| `qwen/qwen2.5-vl-72b-instruct` | ✅ 양호 | 1,960 chars |详细内容 추출 | [output_qwen2.5-vl-72b-instruct.txt](research-data/output_qwen2.5-vl-72b-instruct.txt) |

### 모델별 상세 비교 (Qwen 8B vs 32B)

**핵심 정보 정확도**: 둘 다 동일하게 정확 (호수, 금액, 날짜 등)

**32B에서 추가된 내용**:
1. **표 형식 정리**: 고객번호/업체코드 등을 Markdown 표로 제공
2. **상세 금액 내역**: 전력량료, 기후환경, 연료비조정, 승강기전기료, 공동전기료 등 항목별 상세
3. **세대감면내역 표**: 항목/금액 형태의 구조화된 표
4. **관리비 상세 내역**: 일반관리비, 청소비, 소독비, 승강기유지비, 수선유지비 등 쌍둥이 열 구조
5. **추가 요소**: QR코드, APT Home Service 등

**8B의 제한점**:
- Plain text로 단순 나열만 되어 있음
- 구조화된 데이터 파싱 시 추가 처리 필요
- 누락된 항목: 항목별 세부 금액, 세대감면 상세, APT 할인내역 상세 등

**추천**: 정보 completeness와 구조화 측면에서 **qwen/qwen3-vl-32b-instruct**가最优

- **추천 모델**: `qwen/qwen3-vl-32b-instruct` (품질 대비 효율적)
- **테스트 코드**:
```python
import base64, json
from urllib import request

with open('IMG_7070.jpg', 'rb') as f:
    img_base64 = base64.b64encode(f.read()).decode('utf-8')

payload = {
    'model': 'qwen/qwen3-vl-32b-instruct',  # 최고 품질
    'messages': [{'role': 'user', 'content': [
        {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{img_base64}'}},
        {'type': 'text', 'text': '이 이미지에서 텍스트를 모두 추출해주세요.'}
    ]}],
    'max_tokens': 2048
}
# POST to https://openrouter.ai/api/v1/chat/completions
```

## 다음 단계
- **OpenRouter + qwen/qwen3-vl-32b-instruct**로 이미지 텍스트 추출 가능 (무료)
- 원본 HEIC 파일로도 테스트해볼 수 있음 (현재 JPG 변환 후 테스트)

## MiniMax API를 이용한 파싱 테스트

자세한 내용 및 파싱 결과는 [research-data/management_fee_parsed.md](research-data/management_fee_parsed.md) 참고 (커밋 안됨)