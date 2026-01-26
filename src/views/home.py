import streamlit as st

# --- PAGE TITLE ---  
def show():
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Picnik Web UI", anchor=False)

# --- picknik DESCRIPTION ---
def show_description():
    st.write("\n")
    st.subheader("About Picnik", anchor=False)
    st.write(
        """
        Picnik is a Python package for the extraction of isothermic kinetics data from experimental measurements.
        """
    )

# --- RUN ---
show()
show_description()