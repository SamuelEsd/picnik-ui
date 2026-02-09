"""
Conversion Controls Component

Displays buttons for conversion analysis workflow.
"""

import streamlit as st

from src.utils.SessionManager import SessionManager


class ConversionControls:
    """Component for conversion control buttons."""

    def render(self) -> None:
        """Display buttons for conversion analysis workflow."""
        st.divider()
        st.subheader("Conversion Analysis")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Reset Conversion", type="secondary", key="conversion_reset_btn"):
                SessionManager.set("run_conversion_clicked", False)
                SessionManager.set("conversion_ranges", {})
                SessionManager.set("conversion_plotter", None)
                SessionManager.set("conversion_metadata", None)

                # Clear the button state
                SessionManager.set("run_conversion_clicked", False)
                st.success("Conversion state reset.")

        with col2:
            if st.button("Run Conversion", type="primary", key="conversion_run_btn"):
                SessionManager.set("run_conversion_clicked", True)
