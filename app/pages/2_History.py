import streamlit as st

from app.database import get_all_fees, delete_fee


st.header("📋 처리 기록")

fees = get_all_fees()

if not fees:
    st.info("저장된 관리비 내역이 없습니다.")
else:
    st.write(f"총 {len(fees)}건")

    for fee in fees:
        date = fee.get("date") or "날짜 없음"
        total = fee.get("total_amount")
        total_str = f"{total:,}원" if total is not None else "없음"

        address = f"{fee.get('address_building') or ''} {fee.get('address_unit') or ''}".strip() or "없음"

        elec_kwh = fee.get("electricity_kwh")
        elec_amt = fee.get("electricity_amount")
        elec_str = f"{elec_kwh} kWh ({elec_amt:,}원)" if elec_kwh is not None and elec_amt is not None else "없음"

        water_cbm = fee.get("water_cbm")
        water_amt = fee.get("water_amount")
        water_str = f"{water_cbm} m³ ({water_amt:,}원)" if water_cbm is not None and water_amt is not None else "없음"

        heat_kwh = fee.get("heating_kwh")
        heat_amt = fee.get("heating_amount")
        heat_str = f"{heat_kwh} ({heat_amt:,}원)" if heat_kwh is not None and heat_amt is not None else "없음"

        created = fee.get("created_at", "")[:10] if fee.get("created_at") else "없음"

        with st.expander(f"{date} - {total_str}"):
            st.write(f"**동/호:** {address}")
            st.write(f"**전기:** {elec_str}")
            st.write(f"**수도:** {water_str}")
            st.write(f"**난방:** {heat_str}")
            st.write(f"**생성일:** {created}")

            if st.button(f"삭제", key=f"delete_{fee['id']}"):
                delete_fee(fee['id'])
                st.rerun()
