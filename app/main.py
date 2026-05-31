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