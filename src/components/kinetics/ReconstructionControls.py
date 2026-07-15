"""
Reconstruction Controls Component

Renders the UI controls for g(alpha) reaction model reconstruction.
"""

import streamlit as st

from src.i18n import _
from src.utils.SessionManager import SessionManager
from src.config import SESS_BNUM, SESS_COMP_RESULTS, SESS_RUN_RECON, SESS_RECON_BETA_IDX


class ReconstructionControls:
    """Renders the UI controls for reaction model reconstruction."""

    def render(self) -> None:
        """Display controls for g(alpha) reconstruction."""
        st.divider()
        st.subheader(_("Step 9: Reaction Model Reconstruction — g(α)"))

        if st.session_state.get(SESS_COMP_RESULTS) is None:
            st.info(_("Complete Step 8 (Compensation Effect) first to enable reconstruction."))
            return

        b_num = st.session_state.get(SESS_BNUM)
        if b_num is None:
            return

        col1, col2 = st.columns([3, 1])

        with col1:
            beta_options = {i: _("β = {beta:.2f} K/min").format(beta=b) for i, b in enumerate(b_num)}
            selected_beta_idx = st.selectbox(
                _("Heating rate for temperature integration"),
                options=list(beta_options.keys()),
                format_func=lambda x: beta_options[x],
                help=_(
                    "The reconstruction integrates exp(-E/RT(t))dt along the temperature "
                    "profile of the selected experiment. Using the first (lowest) heating rate "
                    "is common."
                ),
                key="recon_beta_selector",
            )
            st.session_state[SESS_RECON_BETA_IDX] = selected_beta_idx

        with col2:
            st.write("")
            st.write("")
            if st.button(_("Reconstruct g(α)"), type="primary", key="recon_calc_btn"):
                st.session_state[SESS_RUN_RECON] = True
