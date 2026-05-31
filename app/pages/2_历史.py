import streamlit as st
import json

from app.database import get_all_fees, get_fee_by_id, get_raw_data_by_fee_id, delete_fee


st.header("📋 처리 기록")

fees = get_all_fees()

if not fees:
    st.info("저장된 관리비 내역이 없습니다.")
else:
    st.write(f"총 {len(fees)}건")

    for fee in fees:
        with st.expander(f"{fee['date']} - {fee['total_amount']:,}원"):
            st.write(f"**동/호:** {fee['address_building']} {fee['address_unit']}")
            st.write(f"**전기:** {fee['electricity_kwh']} kWh ({fee['electricity_amount']:,}원)")
            st.write(f"**수도:** {fee['water_cbm']} m³ ({fee['water_amount']:,}원)")
            st.write(f"**난방:** {fee['heating_kwh']} ({fee['heating_amount']:,}원)")
            st.write(f"**생성일:** {fee['created_at'][:10]}")

            if st.button(f"삭제", key=f"delete_{fee['id']}"):
                delete_fee(fee['id'])
                st.rerun()