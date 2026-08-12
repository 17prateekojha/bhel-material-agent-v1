import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from datetime import date

from agent.graph import ask_agent
from agent.tools import (
    search_materials_received_today,
    find_reconciliation_exceptions,
)
from database.db import SessionLocal
from database.models import Material


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="BHEL Material Management Agent",
    page_icon="📦",
    layout="wide",
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("📦 BHEL Material Management Agent")
st.caption("BHEL TBG HVDC Nagpur — Material Management")


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select module",
    [
        "🤖 AI Assistant",
        "📊 Dashboard",
        "📦 Materials",
        "📅 Today's Receipts",
        "⚠️ Reconciliation",
    ],
)


# ---------------------------------------------------------
# AI ASSISTANT
# ---------------------------------------------------------

if page == "🤖 AI Assistant":

    st.header("🤖 Material Management AI Assistant")

    st.write(
        "Ask questions about materials, receipts, suppliers, "
        "POs, reconciliation, and store balance."
    )

    question = st.text_area(
        "Enter your question",
        placeholder=(
            "Example: Show all materials received today."
        ),
        height=100,
    )

    if st.button("Ask Agent", type="primary"):

        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Agent is processing..."):
                try:
                    answer = ask_agent(question)

                    st.subheader("Answer")
                    st.write(answer)

                except Exception as exc:
                    st.error("Agent error")
                    st.exception(exc)


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

elif page == "📊 Dashboard":

    st.header("📊 Material Dashboard")

    with SessionLocal() as session:

        materials = session.query(Material).all()

        total_materials = len(materials)

        total_received = sum(
            m.quantity_received or 0
            for m in materials
        )

    # Metrics

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Materials",
            total_materials,
        )

    with col2:
        st.metric(
            "Total Received Quantity",
            total_received,
        )

    st.divider()

    st.subheader("Quick Questions")

    st.info(
        "Use the AI Assistant to ask detailed questions "
        "about material balances, suppliers, POs and reconciliation."
    )


# ---------------------------------------------------------
# MATERIALS
# ---------------------------------------------------------

elif page == "📦 Materials":

    st.header("📦 Material Register")

    search = st.text_input(
        "Search Material ID / PO / Item Code / Description / Supplier"
    )

    with SessionLocal() as session:

        query = session.query(Material)

        if search.strip():

            search_value = f"%{search.strip()}%"

            from sqlalchemy import or_

            query = query.filter(
                or_(
                    Material.material_id.ilike(search_value),
                    Material.po_no.ilike(search_value),
                    Material.item_code.ilike(search_value),
                    Material.description.ilike(search_value),
                    Material.supplier.ilike(search_value),
                )
            )

        rows = query.limit(500).all()

        data = [
            {
                "Material ID": m.material_id,
                "PO": m.po_no,
                "Item Code": m.item_code,
                "Description": m.description,
                "Received": m.quantity_received,
                "Receipt Date": m.receipt_date,
                "GRN": m.grn_no,
                "Store": m.store_location,
                "Supplier": m.supplier,
            }
            for m in rows
        ]

    if data:
        st.dataframe(
            data,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No materials found.")


# ---------------------------------------------------------
# TODAY'S RECEIPTS
# ---------------------------------------------------------

elif page == "📅 Today's Receipts":

    st.header("📅 Materials Received Today")

    st.caption(
        f"Receipt date: {date.today()}"
    )

    try:

        result = search_materials_received_today.invoke({})

        if result.startswith("No materials"):
            st.info(result)
        else:
            st.text(result)

    except Exception as exc:

        st.error("Unable to retrieve today's receipts.")
        st.exception(exc)


# ---------------------------------------------------------
# RECONCILIATION
# ---------------------------------------------------------

elif page == "⚠️ Reconciliation":

    st.header("⚠️ Reconciliation Exceptions")

    try:

        result = find_reconciliation_exceptions.invoke({})

        if result.startswith("No reconciliation"):
            st.success(result)
        else:
            st.error(result)

    except Exception as exc:

        st.error("Unable to retrieve reconciliation data.")
        st.exception(exc)