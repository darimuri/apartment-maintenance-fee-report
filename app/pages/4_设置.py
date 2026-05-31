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