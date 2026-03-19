import streamlit as st

# --- PAGE TITLE ---
def show():
    st.title("Picnik Web UI", anchor=False)


# --- PICNIK DESCRIPTION ---
def show_description():
    st.subheader("About Picnik", anchor=False)
    st.write(
        """
        **Picnik** is a Python package for isoconversional analysis of non-isothermal kinetics from
        thermogravimetric (TGA) data. It computes the activation energy as a function of conversion
        using five established methods:
        """
    )
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            - **OFW** — Ozawa-Flynn-Wall
            - **KAS** — Kissinger-Akahira-Sunose
            - **Fr** — Friedman
            """
        )
    with col2:
        st.markdown(
            """
            - **Vy** — Vyazovkin
            - **aVy** — Advanced Vyazovkin
            """
        )


# --- WORKFLOW GUIDE ---
def show_workflow():
    st.divider()
    st.subheader("How to use this tool", anchor=False)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 1. Tutorial")
        st.write("Learn how to prepare your CSV files and follow a guided example before running your own analysis.")
        if st.button("Go to Tutorial", key="home_btn_tutorial"):
            st.switch_page("src/views/walkthrough.py")
    with col2:
        st.markdown("### 2. Tool")
        st.write("Upload your TGA data files, extract, convert, compute isoconversion tables and activation energies.")
        if st.button("Go to Tool", key="home_btn_tool"):
            st.switch_page("src/views/tool.py")
    with col3:
        st.markdown("### 3. Export")
        st.write("Download your results as CSV files directly from the Tool page after each analysis step.")


# --- RUN ---
show()
show_description()
show_workflow()