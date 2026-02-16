import sys

try:
    import streamlit

    print(f"Streamlit found at: {streamlit.__file__}")
    from streamlit.web import cli

    print("Streamlit CLI module found.")
except ImportError as e:
    print(f"ImportError: {e}")
    print(f"Python path: {sys.path}")
