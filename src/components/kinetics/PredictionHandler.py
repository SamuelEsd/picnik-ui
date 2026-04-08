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
from src.config import (
    SESS_BNUM,
    SESS_ACTIVATION_ENERGY_OBJECT,
    SESS_ACTIVATION_ENERGY_RESULTS,
    SESS_COMP_RESULTS,
    SESS_RECON_RESULTS,
    SESS_PRED_MF_RESULTS,
    SESS_PRED_MB_RESULTS,
    SESS_RUN_PRED_MF,
    SESS_RUN_PRED_MB,
    SESS_PRED_MODE,
    SESS_PRED_ALPHA_TARGET,
    SESS_PRED_BOUNDS,
    SESS_PRED_ISO_T,
    SESS_PRED_LINEAR_B,
    SESS_PRED_MB_ISO_T,
    SESS_PRED_MB_COL,
)
from src.models.results import ModelfreePredictionResults, ModelbasedPredictionResults
from src.components.kinetics.ActivationEnergyHandler import get_active_ae_result


class PredictionHandler:
    """Handles model-free and model-based kinetic predictions."""

    def handle_predictions(self) -> None:
        """Dispatch to the appropriate prediction handler."""
        if SessionManager.get(SESS_RUN_PRED_MF):
            self._handle_modelfree_prediction()

        if SessionManager.get(SESS_RUN_PRED_MB):
            self._handle_modelbased_prediction()

        # Always display stored results
        mf = SessionManager.get(SESS_PRED_MF_RESULTS)
        if mf is not None:
            self._display_modelfree_results(mf)

        mb = SessionManager.get(SESS_PRED_MB_RESULTS)
        if mb is not None:
            self._display_modelbased_results(mb)

    def _handle_modelfree_prediction(self) -> None:
        """Execute model-free prediction."""
        activation_energy_object = SessionManager.get(SESS_ACTIVATION_ENERGY_OBJECT)
        ae_results = get_active_ae_result()

        if activation_energy_object is None or ae_results is None:
            st.error("Activation energy object not available.")
            return

        try:
            E = ae_results.E
            mode = SessionManager.get(SESS_PRED_MODE, "Isothermal")
            alpha_target = float(SessionManager.get(SESS_PRED_ALPHA_TARGET, 0.999))
            bounds = SessionManager.get(SESS_PRED_BOUNDS, (10.0, 10.0))

            with st.spinner(f"Running {mode} model-free prediction..."):
                if mode == "Isothermal":
                    iso_T = float(SessionManager.get(SESS_PRED_ISO_T, 575.0))
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
                    B_val = float(SessionManager.get(SESS_PRED_LINEAR_B, 10.0))
                    a_prime, T_prime, t_prime = (
                        activation_energy_object.modelfree_prediction(
                            E=E,
                            B=B_val,
                            alpha=alpha_target,
                            bounds=bounds,
                        )
                    )

            st.success("Model-free prediction completed")
            SessionManager.set(
                SESS_PRED_MF_RESULTS,
                ModelfreePredictionResults(
                    a_prime=a_prime,
                    T_prime=T_prime,
                    t_prime=t_prime,
                    mode=mode,
                ),
            )

        except Exception as e:
            st.error(f"Error during model-free prediction: {str(e)}")

        SessionManager.set(SESS_RUN_PRED_MF, False)

    def _handle_modelbased_prediction(self) -> None:
        """Execute model-based isothermal prediction using t_isothermal."""
        activation_energy_object = SessionManager.get(SESS_ACTIVATION_ENERGY_OBJECT)
        ae_results = get_active_ae_result()
        comp_results = SessionManager.get(SESS_COMP_RESULTS)
        recon_results = SessionManager.get(SESS_RECON_RESULTS)

        if (
            activation_energy_object is None
            or ae_results is None
            or comp_results is None
            or recon_results is None
        ):
            st.error(
                "Missing data. Ensure Steps 6 (activation energy), "
                "7 (compensation effect), and 8 (reconstruction) are all complete."
            )
            return

        try:
            iso_T = float(SessionManager.get(SESS_PRED_MB_ISO_T, 575.0))
            col = int(SessionManager.get(SESS_PRED_MB_COL, 0))

            with st.spinner(
                f"Running model-based isothermal prediction at T = {iso_T:.0f} K..."
            ):
                t_pred = activation_energy_object.t_isothermal(
                    E=ae_results.E,
                    ln_A=comp_results.ln_A,
                    T0=iso_T,
                    col=col,
                    g_a=recon_results.g_r,
                    alpha=ae_results.alpha,
                )

            st.success("Model-based prediction completed")
            SessionManager.set(
                SESS_PRED_MB_RESULTS,
                ModelbasedPredictionResults(
                    t_pred=t_pred,
                    alpha_values=ae_results.alpha,
                    iso_T=iso_T,
                ),
            )

        except Exception as e:
            st.error(f"Error during model-based prediction: {str(e)}")

        SessionManager.set(SESS_RUN_PRED_MB, False)

    # ------------------------------------------------------------------ #
    # Display helpers                                                       #
    # ------------------------------------------------------------------ #

    def _display_modelfree_results(self, results: ModelfreePredictionResults) -> None:
        """Display model-free prediction results."""
        st.subheader(f"Model-free Prediction — {results.mode}")

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=results.t_prime,
                y=results.a_prime,
                mode="lines+markers",
                marker=dict(size=3),
                name="α(t)",
            )
        )
        fig.update_layout(
            title=f"Predicted Conversion vs Time ({results.mode})",
            xaxis_title="Time [min]",
            yaxis_title="Conversion (α)",
            yaxis_range=[0, 1.05],
            height=400,
        )
        st.plotly_chart(fig, width="stretch")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Final conversion reached", f"{results.a_prime[-1]:.4f}")
        with col2:
            st.metric("Time to final conversion", f"{results.t_prime[-1]:.2f} min")

        df_pred = pd.DataFrame({
            "time [min]": results.t_prime,
            "temperature [K]": results.T_prime,
            "conversion": results.a_prime,
        })
        safe_mode = results.mode.lower().replace(" ", "_")
        st.download_button(
            label="Download Prediction Data (CSV)",
            data=df_pred.to_csv(index=False),
            file_name=f"modelfree_prediction_{safe_mode}.csv",
            mime="text/csv",
            key=f"download_pred_mf_{safe_mode}",
        )

    def _display_modelbased_results(self, results: ModelbasedPredictionResults) -> None:
        """Display model-based isothermal prediction results."""
        st.subheader(f"Model-based Isothermal Prediction — T = {results.iso_T:.0f} K")

        alpha_plot = results.alpha_values[: len(results.t_pred)]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=results.t_pred,
                y=alpha_plot,
                mode="lines+markers",
                marker=dict(size=4, symbol="triangle-left"),
                name=f"T = {results.iso_T:.0f} K",
                line=dict(color="#8B4513"),
            )
        )
        fig.update_layout(
            title=f"Model-based Prediction: α vs Time at T = {results.iso_T:.0f} K",
            xaxis_title="Time [min]",
            yaxis_title="Conversion (α)",
            yaxis_range=[0, 1.05],
            height=400,
        )
        st.plotly_chart(fig, width="stretch")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Final conversion", f"{alpha_plot[-1]:.4f}")
        with col2:
            st.metric("Total time predicted", f"{results.t_pred[-1]:.2f} min")

        df_iso = pd.DataFrame({"time [min]": results.t_pred, "conversion": alpha_plot})
        st.download_button(
            label="Download Isothermal Prediction (CSV)",
            data=df_iso.to_csv(index=False),
            file_name=f"isothermal_prediction_{int(results.iso_T)}K.csv",
            mime="text/csv",
            key="download_pred_mb",
        )
