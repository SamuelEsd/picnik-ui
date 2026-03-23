"""
Reconstruction Controls Component

Renders the UI controls for g(alpha) reaction model reconstruction.
"""

import streamlit as st

from src.utils.SessionManager import SessionManager
from src.config import SESS_BNUM, SESS_COMP_RESULTS


class ReconstructionControls:
    """Renders the UI controls for reaction model reconstruction."""

    def render(self) -> None:
        """Display controls for g(alpha) reconstruction."""
        st.divider()
        st.subheader("Step 9: Reaction Model Reconstruction — g(α)")

        if SessionManager.get(SESS_COMP_RESULTS) is None:
            st.info("Complete Step 8 (Compensation Effect) first to enable reconstruction.")
            return

        b_num = SessionManager.get(SESS_BNUM)
        if b_num is None:
            return

        col1, col2 = st.columns([3, 1])

        with col1:
            beta_options = {i: f"β = {b:.2f} K/min" for i, b in enumerate(b_num)}
            selected_beta_idx = st.selectbox(
                "Heating rate for temperature integration",
                options=list(beta_options.keys()),
                format_func=lambda x: beta_options[x],
                help=(
                    "The reconstruction integrates exp(-E/RT(t))dt along the temperature "
                    "profile of the selected experiment. Using the first (lowest) heating rate "
                    "is common."
                ),
                key="recon_beta_selector",
            )
            SessionManager.set("recon_beta_idx", selected_beta_idx)

        with col2:
            st.write("")
            st.write("")
            if st.button("Reconstruct g(α)", type="primary", key="recon_calc_btn"):
                SessionManager.set("run_recon_clicked", True)
