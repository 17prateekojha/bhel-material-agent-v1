import streamlit as st
from services.reports import create_workbook

def render_reports(session):
    st.subheader("Excel Reports")
    st.write("Generate a consolidated workbook containing material register, events, insurance claims and survey status.")
    if st.button("Generate Excel Workbook", type="primary"):
        path = create_workbook(session)
        with open(path, "rb") as f:
            st.download_button(
                "Download Excel",
                data=f.read(),
                file_name=path.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
