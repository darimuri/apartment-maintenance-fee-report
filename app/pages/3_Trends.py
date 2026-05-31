import streamlit as st
import pandas as pd
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
