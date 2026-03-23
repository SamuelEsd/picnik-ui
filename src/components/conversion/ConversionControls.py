"""
Conversion Controls Component

Displays buttons for conversion analysis workflow.
"""

import streamlit as st

from src.utils.SessionManager import SessionManager
from src.config import SESS_CONVERSION_RANGES, SESS_DATA_EXTRACTOR


class ConversionControls:
    """Component for conversion control buttons."""

    def render(self) -> None:
        """Display buttons for conversion analysis workflow."""
        st.divider()
        st.subheader("Step 5: Conversion Analysis")

        if SessionManager.get(SESS_DATA_EXTRACTOR) is None:
            st.info("Complete Step 3 (Data Extraction) first to enable conversion analysis.")
            return

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Reset Conversion", type="secondary", key="conversion_reset_btn"):
                SessionManager.set("run_conversion_clicked", False)
                SessionManager.set(SESS_CONVERSION_RANGES, {})
                SessionManager.set("conversion_plotter", None)
                SessionManager.set("conversion_metadata", None)
                st.success("Conversion state reset.")

        with col2:
            if st.button("Run Conversion", type="primary", key="conversion_run_btn"):
                SessionManager.set("run_conversion_clicked", True)
