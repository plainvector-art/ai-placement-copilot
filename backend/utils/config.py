import os

def get_secret(key: str, default: str = "") -> str:
    """Gets configuration value from streamlit secrets or environment variables."""
    # 1. Try Streamlit Secrets
    try:
        import streamlit as st
        if key in st.secrets:
            val = str(st.secrets[key])
            if not val.startswith("your_"):
                return val
    except Exception:
        pass
    
    # 2. Try OS Environment
    val = os.getenv(key, default)
    if val.startswith("your_"):
        return ""
    return val
