# streamlit_app/app.py
# Entry point for the Streamlit application.
# This script initializes the session state and builds the main layout.

import streamlit as st
import sys
import os
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from streamlit_app.layout import build_layout
from streamlit_app.state import init_session

def main():
    """
    Main function to run the Streamlit application.
    Initializes the session and builds the UI layout.
    """
    st.set_page_config(layout="wide")
    init_session()  # Initialize session state variables
    build_layout()  # Build the main layout of the application

if __name__ == "__main__":
    # This ensures that main() is called only when the script is executed directly
    main()
    # Start Celery
    celery_proc = subprocess.Popen(
        ["celery", "-A", "celery_worker", "worker", "--loglevel=info"]
    )
