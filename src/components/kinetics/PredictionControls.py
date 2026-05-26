"""
Prediction Controls Component

Renders the UI controls for model-free and model-based kinetic predictions.
"""

import streamlit as st

from src.utils.SessionManager import SessionManager
from src.config import (
    SESS_BNUM, SESS_ACTIVATION_ENERGY_RESULTS, SESS_COMP_RESULTS, SESS_RECON_RESULTS,
    SESS_RUN_PRED_MF, SESS_RUN_PRED_MB,
    SESS_PRED_MODE, SESS_PRED_BOUNDS,
)


class PredictionControls:
    """Renders the UI controls for kinetic predictions."""

    def render(self) -> None:
        """Display prediction controls split across two tabs."""
        st.divider()
        st.subheader("Step 10: Kinetic Predictions")

        ae_results = SessionManager.get_active_ae_result()
        if ae_results is None:
            st.info("Complete Step 7 (Activation Energy) first to enable predictions.")
            return

        tab_mf, tab_mb = st.tabs(["Model-free Prediction", "Model-based Isothermal"])

        with tab_mf:
            self._render_modelfree_controls()

        with tab_mb:
            self._render_modelbased_controls()

    def _render_modelfree_controls(self) -> None:
        """Controls for model-free prediction."""
        mode = st.radio(
            "Temperature program",
            options=["Isothermal", "Linear heating"],
            key="pred_mode_radio",
            help=(
                "Isothermal: hold at a constant temperature. "
                "Linear heating: ramp at a fixed K/min rate."
            ),
        )
        st.session_state[SESS_PRED_MODE] = mode

        col1, col2 = st.columns(2)

        with col1:
            if mode == "Isothermal":
                st.number_input(
                    "Isothermal temperature (K)",
                    min_value=273.0,
                    max_value=2000.0,
                    value=575.0,
                    step=5.0,
                    key="pred_iso_T",
                )
            else:
                st.number_input(
                    "Heating rate β (K/min)",
                    min_value=0.1,
                    max_value=500.0,
                    value=10.0,
                    step=0.5,
                    key="pred_linear_B",
                )

            st.number_input(
                "Target conversion α",
                min_value=0.001,
                max_value=0.999,
                value=0.999,
                step=0.001,
                format="%.3f",
                key="pred_alpha_target",
                help="Simulation runs until this conversion value is reached.",
            )

        with col2:
            st.markdown("**Time search bounds (min)**")
            bounds_lower = st.number_input(
                "Lower bound",
                min_value=0.1,
                max_value=10000.0,
                value=10.0,
                step=1.0,
                key="pred_bounds_lower",
                help=(
                    "Search window around the previous time point. "
                    "Set to the expected order-of-magnitude of the process duration."
                ),
            )
            bounds_upper = st.number_input(
                "Upper bound",
                min_value=0.1,
                max_value=10000.0,
                value=10.0,
                step=1.0,
                key="pred_bounds_upper",
            )
            st.session_state[SESS_PRED_BOUNDS] = (bounds_lower, bounds_upper)

        st.write("")
        if st.button("Run Model-free Prediction", type="primary", key="pred_mf_run_btn"):
            st.session_state[SESS_RUN_PRED_MF] = True

    def _render_modelbased_controls(self) -> None:
        """Controls for model-based isothermal prediction."""
        if st.session_state.get(SESS_COMP_RESULTS) is None or st.session_state.get(SESS_RECON_RESULTS) is None:
            st.info(
                "Complete Steps 8 (Compensation Effect) and 9 (Reconstruction) "
                "to enable model-based predictions."
            )
            return

        b_num = st.session_state.get(SESS_BNUM)

        col1, col2 = st.columns(2)
        with col1:
            st.number_input(
                "Isothermal temperature (K)",
                min_value=273.0,
                max_value=2000.0,
                value=575.0,
                step=5.0,
                key="pred_mb_iso_T",
                help="Constant temperature at which to predict conversion vs time.",
            )

            if b_num is not None:
                beta_options = {i: f"β = {b:.2f} K/min" for i, b in enumerate(b_num)}
                st.selectbox(
                    "Reference heating rate",
                    options=list(beta_options.keys()),
                    format_func=lambda x: beta_options[x],
                    key="pred_mb_col",
                    help="Heating rate whose temperature profile is used for the integral.",
                )

        with col2:
            st.write("")

        if st.button("Run Model-based Prediction", type="primary", key="pred_mb_run_btn"):
            st.session_state[SESS_RUN_PRED_MB] = True
