"""
Extraction Controls Component

Displays buttons for data extraction workflow.
"""

import streamlit as st

from src.utils.SessionManager import SessionManager
from src.config import SESS_EXTRACT_CLICKED


class ExtractionControls:
    """Component for extraction control buttons."""

    def render(self) -> None:
        """Display Reset and Extract Data buttons."""
        st.divider()
        st.subheader("Step 3: Data Extraction")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Reset All", type="secondary", key="workflow_reset_btn"):
                SessionManager.clear_extraction_state()
                st.success("Application reset. Reload the page to start fresh.")

        with col2:
            if st.button("Extract Data", type="primary", key="workflow_extract_btn"):
                SessionManager.set(SESS_EXTRACT_CLICKED, True)
