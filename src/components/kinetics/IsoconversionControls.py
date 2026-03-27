"""
Isoconversion Controls Component

Renders the UI controls for isoconversion analysis (Step 6).
"""

import streamlit as st

from src.utils.SessionManager import SessionManager
from src.config import DEFAULT_ISO_DA, SESS_CONVERSION_METADATA, SESS_RUN_ISOCONVERSION, SESS_ISO_DA


class IsoconversionControls:
    """Renders the UI controls for isoconversion analysis."""

    def render(self) -> None:
        """Display isoconversion parameter controls."""
        st.divider()
        st.subheader("Step 6: Isoconversion Analysis")

        if SessionManager.get(SESS_CONVERSION_METADATA) is None:
            st.info("Complete Step 5 (Conversion) first to enable isoconversion analysis.")
            return

        col1, col2 = st.columns([3, 1])

        with col1:
            d_a = st.slider(
                "Conversion step size (∆α)",
                min_value=0.001,
                max_value=0.1,
                value=SessionManager.get(SESS_ISO_DA, DEFAULT_ISO_DA),
                step=0.001,
                help="Step size between conversion values for isoconversion calculations",
                key="isoconv_d_a_slider",
            )
            SessionManager.set(SESS_ISO_DA, d_a)

        with col2:
            st.write("")
            st.write("")
            if st.button("Run Isoconversion", type="primary", key="isoconv_run_btn"):
                SessionManager.set(SESS_RUN_ISOCONVERSION, True)
