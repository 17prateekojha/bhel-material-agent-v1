import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from database.db import init_db, SessionLocal
from ui.dashboard import render_dashboard
from ui.material_entry import render_material_entry
from ui.events import render_events
from ui.reconciliation import render_reconciliation
from ui.reports import render_reports

st.set_page_config(page_title="BHEL HVDC Nagpur Material Agent", page_icon="📦", layout="wide")
init_db()

st.title("📦 BHEL TBG HVDC Nagpur — Material Management Agent")

with SessionLocal() as session:
    page = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Daily Receipt", "Movement / Damage", "Reconciliation", "Excel Reports", "AI Agent"]
    )

    if page == "Dashboard":
        render_dashboard(session)
    elif page == "Daily Receipt":
        render_material_entry(session)
    elif page == "Movement / Damage":
        render_events(session)
    elif page == "Reconciliation":
        render_reconciliation(session)
    elif page == "Excel Reports":
        render_reports(session)
    elif page == "AI Agent":
        st.subheader("🤖 Material Management AI Agent")
        st.caption("Ask questions about material records and reconciliation.")
        question = st.text_area(
            "Ask the agent",
            placeholder="Example: Show MAT-000001.\nOr: Find reconciliation exceptions."
        )
        if st.button("Ask Agent", type="primary") and question.strip():
            with st.spinner("Agent is working..."):
                try:
                    from agent.graph import ask_agent
                    st.write(ask_agent(question))
                except Exception as exc:
                    st.error(
                        "AI Agent could not connect. Make sure Ollama is running and "
                        f"the configured model is available. Details: {exc}"
                    )
