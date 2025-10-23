import streamlit as st

# --- PAGES SETUP ---
home_page = st.Page(
    "views/home.py",
    title="Inicio",
    icon=":material/account_circle:",
    default=True,
)
walkthrough_page = st.Page(
    "views/walkthrough.py",
    title="Tutorial",
    icon=":material/bar_chart:",
)
tool_page = st.Page(
    "views/tool.py",
    title="Herramienta",
    icon=":material/smart_toy:",
)

# --- NAVIGATION SETUP ---
pg = st.navigation(pages=[home_page, walkthrough_page, tool_page])

# --- RUN UI ---
pg.run()