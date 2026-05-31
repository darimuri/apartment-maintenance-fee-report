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
