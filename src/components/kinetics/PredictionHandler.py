"""
Prediction Handler Component

Provides two types of kinetic predictions:

1. Model-free prediction  (modelfree_prediction)
   Based on the isoconversional principle: J[E_alpha, T(t)_i] = J[E_alpha, T(t)_j]
   Works for isothermal, linear heating, or custom temperature programs.
   Requires only activation energy — no reaction model needed.

2. Model-based isothermal prediction  (t_isothermal)
   Uses the kinetic triplet (E, A, g(alpha)) to predict time-to-conversion at
   a constant temperature.  Requires Steps 7 + 8 (compensation effect + reconstruction).

This is Step 9 in the pICNIK workflow.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.utils.SessionManager import SessionManager
from src.config import SESS_BNUM, SESS_ACTIVATION_ENERGY_OBJECT, SESS_ACTIVATION_ENERGY_RESULTS, SESS_COMP_LN_A


class PredictionHandler:
    """Handles model-free and model-based kinetic predictions."""

    # ------------------------------------------------------------------ #
    # Controls                                                             #
    # ------------------------------------------------------------------ #

    def render_prediction_controls(self) -> None:
        """Display prediction controls split across two tabs."""
        st.divider()
        st.subheader("Step 9: Kinetic Predictions")

        ae_results = SessionManager.get(SESS_ACTIVATION_ENERGY_RESULTS)
        if ae_results is None:
            st.info("Complete Step 6 (Activation Energy) first to enable predictions.")
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
        SessionManager.set("pred_mode", mode)

        col1, col2 = st.columns(2)

        with col1:
            if mode == "Isothermal":
                iso_T = st.number_input(
                    "Isothermal temperature (K)",
                    min_value=273.0,
                    max_value=2000.0,
                    value=575.0,
                    step=5.0,
                    key="pred_iso_T",
                )
                SessionManager.set("pred_iso_T", iso_T)
            else:
                linear_B = st.number_input(
                    "Heating rate β (K/min)",
                    min_value=0.1,
                    max_value=500.0,
                    value=10.0,
                    step=0.5,
                    key="pred_linear_B",
                )
                SessionManager.set("pred_linear_B", linear_B)

            alpha_target = st.number_input(
                "Target conversion α",
                min_value=0.001,
                max_value=0.999,
                value=0.999,
                step=0.001,
                format="%.3f",
                key="pred_alpha_target",
                help="Simulation runs until this conversion value is reached.",
            )
            SessionManager.set("pred_alpha_target", alpha_target)

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
            SessionManager.set("pred_bounds", (bounds_lower, bounds_upper))

        st.write("")
        if st.button(
            "Run Model-free Prediction", type="primary", key="pred_mf_run_btn"
        ):
            SessionManager.set("run_pred_mf_clicked", True)

    def _render_modelbased_controls(self) -> None:
        """Controls for model-based isothermal prediction."""
        g_r = SessionManager.get("recon_g_r")
        ln_A = SessionManager.get(SESS_COMP_LN_A)

        if g_r is None or ln_A is None:
            st.info(
                "Complete Steps 7 (Compensation Effect) and 8 (Reconstruction) "
                "to enable model-based predictions."
            )
            return

        b_num = SessionManager.get(SESS_BNUM)

        col1, col2 = st.columns(2)
        with col1:
            mb_iso_T = st.number_input(
                "Isothermal temperature (K)",
                min_value=273.0,
                max_value=2000.0,
                value=575.0,
                step=5.0,
                key="pred_mb_iso_T",
                help="Constant temperature at which to predict conversion vs time.",
            )
            SessionManager.set("pred_mb_iso_T", mb_iso_T)

            if b_num is not None:
                beta_options = {i: f"β = {b:.2f} K/min" for i, b in enumerate(b_num)}
                mb_col = st.selectbox(
                    "Reference heating rate",
                    options=list(beta_options.keys()),
                    format_func=lambda x: beta_options[x],
                    key="pred_mb_col",
                    help="Heating rate whose temperature profile is used for the integral.",
                )
                SessionManager.set("pred_mb_col", mb_col)

        with col2:
            st.write("")

        if st.button(
            "Run Model-based Prediction", type="primary", key="pred_mb_run_btn"
        ):
            SessionManager.set("run_pred_mb_clicked", True)

    # ------------------------------------------------------------------ #
    # Handlers                                                             #
    # ------------------------------------------------------------------ #

    def handle_predictions(self) -> None:
        """Dispatch to the appropriate prediction handler."""
        if SessionManager.get("run_pred_mf_clicked"):
            self._handle_modelfree_prediction()

        if SessionManager.get("run_pred_mb_clicked"):
            self._handle_modelbased_prediction()

    def _handle_modelfree_prediction(self) -> None:
        """Execute model-free prediction."""
        activation_energy_object = SessionManager.get(SESS_ACTIVATION_ENERGY_OBJECT)
        ae_results = SessionManager.get(SESS_ACTIVATION_ENERGY_RESULTS)

        if activation_energy_object is None or ae_results is None:
            st.error("Activation energy object not available.")
            return

        try:
            result = ae_results["result"]
            E = np.array(result[2])
            mode = SessionManager.get("pred_mode", "Isothermal")
            alpha_target = float(SessionManager.get("pred_alpha_target", 0.999))
            bounds = SessionManager.get("pred_bounds", (10.0, 10.0))

            with st.spinner(f"Running {mode} model-free prediction..."):
                if mode == "Isothermal":
                    iso_T = float(SessionManager.get("pred_iso_T", 575.0))
                    a_prime, T_prime, t_prime = (
                        activation_energy_object.modelfree_prediction(
                            E=E,
                            B=0,
                            isoT=iso_T,
                            alpha=alpha_target,
                            bounds=bounds,
                        )
                    )
                else:
                    B_val = float(SessionManager.get("pred_linear_B", 10.0))
                    a_prime, T_prime, t_prime = (
                        activation_energy_object.modelfree_prediction(
                            E=E,
                            B=B_val,
                            alpha=alpha_target,
                            bounds=bounds,
                        )
                    )

            st.success("Model-free prediction completed")
            self._display_modelfree_results(a_prime, T_prime, t_prime, mode)
            SessionManager.set("run_pred_mf_clicked", False)

        except Exception as e:
            st.error(f"Error during model-free prediction: {str(e)}")
            SessionManager.set("run_pred_mf_clicked", False)

    def _handle_modelbased_prediction(self) -> None:
        """Execute model-based isothermal prediction using t_isothermal."""
        activation_energy_object = SessionManager.get(SESS_ACTIVATION_ENERGY_OBJECT)
        ae_results = SessionManager.get(SESS_ACTIVATION_ENERGY_RESULTS)
        g_r = SessionManager.get("recon_g_r")
        ln_A = SessionManager.get(SESS_COMP_LN_A)

        if (
            activation_energy_object is None
            or ae_results is None
            or g_r is None
            or ln_A is None
        ):
            st.error(
                "Missing data. Ensure Steps 6 (activation energy), "
                "7 (compensation effect), and 8 (reconstruction) are all complete."
            )
            return

        try:
            result = ae_results["result"]
            E = np.array(result[2])
            alpha_values = np.array(result[0])
            iso_T = float(SessionManager.get("pred_mb_iso_T", 575.0))
            col = int(SessionManager.get("pred_mb_col", 0))

            with st.spinner(
                f"Running model-based isothermal prediction at T = {iso_T:.0f} K..."
            ):
                t_pred = activation_energy_object.t_isothermal(
                    E=E,
                    ln_A=ln_A,
                    T0=iso_T,
                    col=col,
                    g_a=g_r,
                    alpha=alpha_values,
                )

            st.success("Model-based prediction completed")
            self._display_modelbased_results(t_pred, alpha_values, iso_T)
            SessionManager.set("run_pred_mb_clicked", False)

        except Exception as e:
            st.error(f"Error during model-based prediction: {str(e)}")
            SessionManager.set("run_pred_mb_clicked", False)

    # ------------------------------------------------------------------ #
    # Display helpers                                                       #
    # ------------------------------------------------------------------ #

    def _display_modelfree_results(
        self, a_prime, T_prime, t_prime, mode: str
    ) -> None:
        """Display model-free prediction results."""
        st.subheader(f"Model-free Prediction — {mode}")

        # α vs time
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=t_prime,
                y=a_prime,
                mode="lines+markers",
                marker=dict(size=3),
                name="α(t)",
            )
        )
        fig.update_layout(
            title=f"Predicted Conversion vs Time ({mode})",
            xaxis_title="Time [min]",
            yaxis_title="Conversion (α)",
            yaxis_range=[0, 1.05],
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Final conversion reached", f"{a_prime[-1]:.4f}")
        with col2:
            st.metric("Time to final conversion", f"{t_prime[-1]:.2f} min")

        # Download
        df_pred = pd.DataFrame(
            {
                "time [min]": t_prime,
                "temperature [K]": T_prime,
                "conversion": a_prime,
            }
        )
        safe_mode = mode.lower().replace(" ", "_")
        st.download_button(
            label="Download Prediction Data (CSV)",
            data=df_pred.to_csv(index=False),
            file_name=f"modelfree_prediction_{safe_mode}.csv",
            mime="text/csv",
            key=f"download_pred_mf_{safe_mode}",
        )

    def _display_modelbased_results(
        self, t_pred, alpha_values, iso_T: float
    ) -> None:
        """Display model-based isothermal prediction results."""
        st.subheader(f"Model-based Isothermal Prediction — T = {iso_T:.0f} K")

        alpha_plot = alpha_values[: len(t_pred)]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=t_pred,
                y=alpha_plot,
                mode="lines+markers",
                marker=dict(size=4, symbol="triangle-left"),
                name=f"T = {iso_T:.0f} K",
                line=dict(color="#8B4513"),
            )
        )
        fig.update_layout(
            title=f"Model-based Prediction: α vs Time at T = {iso_T:.0f} K",
            xaxis_title="Time [min]",
            yaxis_title="Conversion (α)",
            yaxis_range=[0, 1.05],
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Final conversion", f"{alpha_plot[-1]:.4f}")
        with col2:
            st.metric("Total time predicted", f"{t_pred[-1]:.2f} min")

        df_iso = pd.DataFrame(
            {"time [min]": t_pred, "conversion": alpha_plot}
        )
        st.download_button(
            label="Download Isothermal Prediction (CSV)",
            data=df_iso.to_csv(index=False),
            file_name=f"isothermal_prediction_{int(iso_T)}K.csv",
            mime="text/csv",
            key="download_pred_mb",
        )
