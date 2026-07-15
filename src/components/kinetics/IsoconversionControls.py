"""
Isoconversion Controls Component

Renders the UI controls for isoconversion analysis (Step 6).
"""

import streamlit as st

from src.i18n import _
from src.utils.SessionManager import SessionManager
from src.config import DEFAULT_ISO_DA, SESS_CONVERSION_METADATA, SESS_RUN_ISOCONVERSION, SESS_ISO_DA


_SLIDER_KEY = "isoconv_d_a_slider"
_INPUT_KEY = "isoconv_d_a_input"


def _sync_from_slider() -> None:
    st.session_state[SESS_ISO_DA] = st.session_state[_SLIDER_KEY]
    st.session_state[_INPUT_KEY] = st.session_state[_SLIDER_KEY]


def _sync_from_input() -> None:
    st.session_state[SESS_ISO_DA] = st.session_state[_INPUT_KEY]
    st.session_state[_SLIDER_KEY] = st.session_state[_INPUT_KEY]


class IsoconversionControls:
    """Renders the UI controls for isoconversion analysis."""

    def render(self) -> None:
        """Display isoconversion parameter controls."""
        st.divider()
        st.subheader(_("Step 6: Isoconversion Analysis"))

        if st.session_state.get(SESS_CONVERSION_METADATA) is None:
            st.info(_("Complete Step 5 (Conversion) first to enable isoconversion analysis."))
            return

        current_d_a = st.session_state.get(SESS_ISO_DA, DEFAULT_ISO_DA)
        st.session_state.setdefault(_SLIDER_KEY, current_d_a)
        st.session_state.setdefault(_INPUT_KEY, current_d_a)

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.slider(
                _("Conversion step size (∆α)"),
                min_value=0.001,
                max_value=0.1,
                step=0.001,
                format="%.3f",
                help=_("Step size between conversion values for isoconversion calculations"),
                key=_SLIDER_KEY,
                on_change=_sync_from_slider,
            )

        with col2:
            st.number_input(
                _("Exact value"),
                min_value=0.001,
                max_value=0.1,
                step=0.001,
                format="%.3f",
                help=_("Type a precise ∆α value — useful for values below 0.01, hard to hit with the slider."),
                key=_INPUT_KEY,
                on_change=_sync_from_input,
            )

        with col3:
            st.write("")
            st.write("")
            if st.button(_("Run Isoconversion"), type="primary", key="isoconv_run_btn"):
                st.session_state[SESS_RUN_ISOCONVERSION] = True
