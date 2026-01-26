"""
Picnik UI - Main application entry point
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
from src.config import APP_TITLE, APP_ICON

# Configure page settings
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PAGES SETUP ---
home_page = st.Page(
    "src/views/home.py",
    title="Inicio",
    icon=":material/account_circle:",
    default=True,
)

walkthrough_page = st.Page(
    "src/views/walkthrough.py",
    title="Tutorial",
    icon=":material/bar_chart:",
)

tool_page = st.Page(
    "src/views/tool.py",
    title="Herramienta",
    icon=":material/smart_toy:",
)

# --- NAVIGATION SETUP ---
pg = st.navigation(pages=[home_page, walkthrough_page, tool_page])

# --- RUN UI ---
pg.run()
