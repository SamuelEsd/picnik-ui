"""
Compensation Effect Controls Component

Renders the UI controls for the compensation effect calculation.
"""

import streamlit as st

from src.utils.SessionManager import SessionManager
from src.config import SESS_BNUM, SESS_ACTIVATION_ENERGY_RESULTS, SESS_RUN_COMP, SESS_COMP_COL


class CompensationEffectControls:
    """Renders the UI controls for compensation effect calculation."""

    def render(self) -> None:
        """Display controls for compensation effect calculation."""
        st.divider()
        st.subheader("Step 8: Pre-exponential Factor — Compensation Effect")

        ae_results = SessionManager.get(SESS_ACTIVATION_ENERGY_RESULTS)
        if ae_results is None:
            st.info("Complete Step 7 (Activation Energy) first to enable this step.")
            return

        b_num = SessionManager.get(SESS_BNUM)
        if b_num is None:
            st.info("Heating rate data not available.")
            return

        col1, col2 = st.columns([3, 1])

        with col1:
            beta_options = {
                i: f"β = {b:.2f} K/min (column {i})"
                for i, b in enumerate(b_num)
            }
            selected_col = st.selectbox(
                "Reference heating rate for model fitting",
                options=list(beta_options.keys()),
                format_func=lambda x: beta_options[x],
                help=(
                    "The compensation effect fits reaction models to data at this heating rate. "
                    "The last (highest) heating rate often gives the best signal."
                ),
                key="comp_col_selector",
            )
            SessionManager.set(SESS_COMP_COL, selected_col)

        with col2:
            st.write("")
            st.write("")
            if st.button(
                "Calculate Compensation Effect",
                type="primary",
                key="comp_calc_btn",
            ):
                SessionManager.set(SESS_RUN_COMP, True)
