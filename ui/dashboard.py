import streamlit as st
from sqlalchemy import func
from database.models import Material, MaterialEvent, InsuranceClaim, Survey
from services.material_service import material_balance
from services.reconciliation import exceptions

def render_dashboard(session):
    materials = session.query(Material).all()
    received = sum(material_balance(session, m)["received"] for m in materials)
    store = sum(material_balance(session, m)["store"] for m in materials)
    handed = sum(material_balance(session, m)["handed_over"] for m in materials)
    damaged = sum(material_balance(session, m)["damaged"] for m in materials)
    exc = len(exceptions(session))

    st.subheader("BHEL TBG HVDC Nagpur — Material Dashboard")
    a,b,c,d,e = st.columns(5)
    a.metric("Materials", len(materials))
    b.metric("Received Qty", received)
    c.metric("Store Balance", store)
    d.metric("Handed Over", handed)
    e.metric("Exceptions", exc)

    if exc:
        st.warning(f"{exc} reconciliation exception(s) require attention.")
    else:
        st.success("No reconciliation exceptions found.")
