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

    def handle_predictions(self) -> None:
        """Dispatch to the appropriate prediction handler."""
        if SessionManager.get("run_pred_mf_clicked"):
            self._handle_modelfree_prediction()

        if SessionManager.get("run_pred_mb_clicked"):
            self._handle_modelbased_prediction()

        # Always display stored results
        mf = SessionManager.get("pred_mf_results")
        if mf is not None:
            self._display_modelfree_results(mf["a_prime"], mf["T_prime"], mf["t_prime"], mf["mode"])

        mb = SessionManager.get("pred_mb_results")
        if mb is not None:
            self._display_modelbased_results(mb["t_pred"], mb["alpha_values"], mb["iso_T"])

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
            SessionManager.set("pred_mf_results", {
                "a_prime": a_prime,
                "T_prime": T_prime,
                "t_prime": t_prime,
                "mode": mode,
            })

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
            SessionManager.set("pred_mb_results", {
                "t_pred": t_pred,
                "alpha_values": alpha_values,
                "iso_T": iso_T,
            })

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
