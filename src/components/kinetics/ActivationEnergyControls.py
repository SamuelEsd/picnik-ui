"""
Activation Energy Controls Component

Renders the UI controls for activation energy method selection.
"""

import streamlit as st

from src.utils.SessionManager import SessionManager

AE_METHODS = {
    "Fr": "Friedman method",
    "KAS": "Kissinger-Akahira-Sunose method",
    "OFW": "Osawa-Flynn-Wall method",
    "Vy": "Vyazovkin method",
    "aVy": "Advanced Vyazovkin method",
}


class ActivationEnergyControls:
    """Renders the UI controls for activation energy method selection."""

    def render(self) -> None:
        """Display activation energy method selection controls."""
        st.divider()
        st.subheader("Step 7: Activation Energy Analysis")

        if SessionManager.get("isoconversion_results") is None:
            st.info("Complete Step 6 (Isoconversion) first to enable activation energy analysis.")
            return

        st.write("**Choose the method to use for activation energy calculation:**")

        col1, col2 = st.columns([3, 1])

        with col1:
            selected_method = st.selectbox(
                "Select Activation Energy Method",
                options=list(AE_METHODS.keys()),
                format_func=lambda x: AE_METHODS[x],
                help="Select one of the five available isoconversional methods for activation energy calculation",
                key="ae_method_selectbox",
            )
            SessionManager.set("selected_ae_method", selected_method)

            if selected_method == "aVy":
                p_value = st.slider(
                    "P value (Advanced Vyazovkin)",
                    min_value=0.50,
                    max_value=0.99,
                    step=0.01,
                    value=SessionManager.get("avy_p_value", 0.50),
                    help="Set the P parameter for Advanced Vyazovkin method (0.50 to 0.99)",
                    key="avy_p_slider",
                )
                SessionManager.set("avy_p_value", p_value)

        with col2:
            st.write("")
            st.write("")
            if st.button(
                "Calculate Activation Energy",
                type="primary",
                key="ae_calculate_btn",
            ):
                SessionManager.set("run_ae_clicked", True)
