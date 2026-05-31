import streamlit as st
from app.database import init_db

st.set_page_config(
    page_title="아파트 관리비 분석",
    page_icon="📊",
    layout="wide"
)

init_db()

# 커스텀 네비게이션으로 한국어 메뉴 표시
pg = st.navigation([
    st.Page("pages/1_Upload.py", title="📤 업로드", icon="📤"),
    st.Page("pages/2_History.py", title="📋 이력", icon="📋"),
    st.Page("pages/3_Trends.py", title="📈 추이", icon="📈"),
    st.Page("pages/4_Settings.py", title="⚙️ 설정", icon="⚙️"),
])
pg.run()
