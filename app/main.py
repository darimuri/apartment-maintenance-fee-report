import logging
import streamlit as st

from app.database import init_db

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

st.set_page_config(
    page_title="아파트 관리비 분석",
    page_icon="📊",
    layout="wide"
)

init_db()

# 커스텀 네비게이션으로 한국어 메뉴 표시
pg = st.navigation([
    st.Page("pages/1_Upload.py", title="업로드"),
    st.Page("pages/2_History.py", title="이력"),
    st.Page("pages/3_Trends.py", title="추이"),
    st.Page("pages/4_Settings.py", title="설정"),
])
pg.run()
