import os

from dotenv import load_dotenv

load_dotenv()


try:
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    st = None


def get_setting(name, default=None):
    # Streamlit Cloud secrets
    if st is not None:
        try:
            if hasattr(st, "secrets") and name in st.secrets:
                return st.secrets[name]
        except Exception:
            pass

    # Local .env / environment variables
    return os.getenv(name, default)
