import sys
from streamlit.web import cli
import os

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        "streamlit_app.py",
        "--server.headless",
        "true",
        "--server.port",
        "8501",
    ]
    sys.exit(cli.main())
