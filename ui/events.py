import streamlit as st
from datetime import date
from database.models import Material
from services.material_service import add_event

def render_events(session):
    st.subheader("Material Movement / Damage / Shortage")
    materials = session.query(Material).order_by(Material.material_id).all()
    if not materials:
        st.info("Add a material first.")
        return

    labels = {m.material_id: f"{m.material_id} — {m.description}" for m in materials}
    material_id = st.selectbox("Material", list(labels), format_func=lambda x: labels[x])
    event_type = st.selectbox("Event", ["HANDOVER", "DAMAGE", "SHORTAGE"])
    c1,c2,c3 = st.columns(3)
    event_date = c1.date_input("Event Date", value=date.today())
    qty = c2.number_input("Quantity", min_value=0.0, step=1.0)
    party = c3.text_input("Handed To / Responsible Party")
    ref = st.text_input("Reference No")
    remarks = st.text_area("Remarks")
    if st.button("Save Event", type="primary"):
        if qty <= 0:
            st.error("Quantity must be greater than zero.")
            return
        try:
            add_event(session, material_id, event_date, event_type, qty, party, ref, remarks)
            st.success("Event saved.")
        except Exception as exc:
            session.rollback()
            st.error(str(exc))
