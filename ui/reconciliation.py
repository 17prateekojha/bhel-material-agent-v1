import streamlit as st
import pandas as pd
from services.reconciliation import reconcile_all

def render_reconciliation(session):
    st.subheader("Material Reconciliation")
    rows = reconcile_all(session)
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("No material records available.")
        return
    st.dataframe(df, use_container_width=True, hide_index=True)
    bad = df[df["Status"] == "EXCEPTION"]
    if not bad.empty:
        st.error(f"{len(bad)} exception(s) found.")
    else:
        st.success("All material records reconcile.")
