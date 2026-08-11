import os

try:
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    st = None


def get_setting(name, default=None):
    if st is not None:
        try:
            if hasattr(st, "secrets") and name in st.secrets:
                return st.secrets[name]
        except Exception:
            pass

    return os.getenv(name, default)
