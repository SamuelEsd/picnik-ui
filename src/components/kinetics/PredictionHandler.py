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

from src.i18n import _
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


class PredictionHandler:
    """Handles model-free and model-based kinetic predictions."""

    def handle_predictions(self) -> None:
        """Dispatch model-free and model-based predictions and display stored results.

        Checks SESS_RUN_PRED_MF and SESS_RUN_PRED_MB independently, so both
        predictions can be triggered and displayed in the same render cycle.
        Always renders any results already stored in session at the end of the call.
        """
        if st.session_state.get(SESS_RUN_PRED_MF):
            self._handle_modelfree_prediction()

        if st.session_state.get(SESS_RUN_PRED_MB):
            self._handle_modelbased_prediction()

        # Always display stored results
        mf = st.session_state.get(SESS_PRED_MF_RESULTS)
        if mf is not None:
            self._display_modelfree_results(mf)

        mb = st.session_state.get(SESS_PRED_MB_RESULTS)
        if mb is not None:
            self._display_modelbased_results(mb)

    def _handle_modelfree_prediction(self) -> None:
        """Run modelfree_prediction() for isothermal or linear-ramp temperature programs.

        Reads mode, temperature/rate, alpha target, and solver bounds from session.
        Stores a ModelfreePredictionResults on success. Does not require a reaction
        model — only E(α) from the active activation energy method is needed.
        """
        activation_energy_object = st.session_state.get(SESS_ACTIVATION_ENERGY_OBJECT)
        ae_results = SessionManager.get_active_ae_result()

        if activation_energy_object is None or ae_results is None:
            st.error(_("Activation energy object not available."))
            return

        try:
            E = ae_results.E
            mode = st.session_state.get(SESS_PRED_MODE, "Isothermal")
            mode_label = _("Isothermal") if mode == "Isothermal" else _("Linear heating")
            alpha_target = float(st.session_state.get(SESS_PRED_ALPHA_TARGET, 0.999))
            bounds = st.session_state.get(SESS_PRED_BOUNDS, (10.0, 10.0))

            with st.spinner(_("Running {mode} model-free prediction...").format(mode=mode_label)):
                if mode == "Isothermal":
                    iso_T = float(st.session_state.get(SESS_PRED_ISO_T, 575.0))
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
                    B_val = float(st.session_state.get(SESS_PRED_LINEAR_B, 10.0))
                    a_prime, T_prime, t_prime = (
                        activation_energy_object.modelfree_prediction(
                            E=E,
                            B=B_val,
                            alpha=alpha_target,
                            bounds=bounds,
                        )
                    )

            st.success(_("Model-free prediction completed"))
            st.session_state[SESS_PRED_MF_RESULTS] = ModelfreePredictionResults(
                    a_prime=a_prime,
                    T_prime=T_prime,
                    t_prime=t_prime,
                    mode=mode,
                )

        except Exception as e:
            st.error(_("Error during model-free prediction: {error}").format(error=str(e)))

        st.session_state[SESS_RUN_PRED_MF] = False

    def _handle_modelbased_prediction(self) -> None:
        """Run t_isothermal() to predict time-to-conversion at a constant temperature.

        Requires the full kinetic triplet: E(α) from the active method, ln(A) from
        the compensation effect step, and g(α) from the reconstruction step.
        Stores a ModelbasedPredictionResults on success.
        """
        activation_energy_object = st.session_state.get(SESS_ACTIVATION_ENERGY_OBJECT)
        ae_results = SessionManager.get_active_ae_result()
        comp_results = st.session_state.get(SESS_COMP_RESULTS)
        recon_results = st.session_state.get(SESS_RECON_RESULTS)

        if (
            activation_energy_object is None
            or ae_results is None
            or comp_results is None
            or recon_results is None
        ):
            st.error(
                _(
                    "Missing data. Ensure Steps 6 (activation energy), "
                    "7 (compensation effect), and 8 (reconstruction) are all complete."
                )
            )
            return

        try:
            iso_T = float(st.session_state.get(SESS_PRED_MB_ISO_T, 575.0))
            col = int(st.session_state.get(SESS_PRED_MB_COL, 0))

            with st.spinner(
                _("Running model-based isothermal prediction at T = {iso_T:.0f} K...").format(iso_T=iso_T)
            ):
                t_pred = activation_energy_object.t_isothermal(
                    E=ae_results.E,
                    ln_A=comp_results.ln_A,
                    T0=iso_T,
                    col=col,
                    g_a=recon_results.g_r,
                    alpha=ae_results.alpha,
                )

            st.success(_("Model-based prediction completed"))
            st.session_state[SESS_PRED_MB_RESULTS] = ModelbasedPredictionResults(
                    t_pred=t_pred,
                    alpha_values=ae_results.alpha,
                    iso_T=iso_T,
                )

        except Exception as e:
            st.error(_("Error during model-based prediction: {error}").format(error=str(e)))

        st.session_state[SESS_RUN_PRED_MB] = False

    # ------------------------------------------------------------------ #
    # Display helpers                                                       #
    # ------------------------------------------------------------------ #

    def _display_modelfree_results(self, results: ModelfreePredictionResults) -> None:
        """Render α(t) chart, summary metrics, and CSV download for model-free prediction.

        Args:
            results: Stored model-free prediction output containing predicted
                conversion, temperature, and time arrays, plus the temperature mode.
        """
        mode_label = _("Isothermal") if results.mode == "Isothermal" else _("Linear heating")
        st.subheader(_("Model-free Prediction — {mode}").format(mode=mode_label))

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
            title=_("Predicted Conversion vs Time ({mode})").format(mode=mode_label),
            xaxis_title=_("Time [min]"),
            yaxis_title=_("Conversion (α)"),
            yaxis_range=[0, 1.05],
            height=400,
        )
        st.plotly_chart(fig, width="stretch")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(_("Final conversion reached"), f"{results.a_prime[-1]:.4f}")
        with col2:
            st.metric(_("Time to final conversion"), f"{results.t_prime[-1]:.2f} min")

        df_pred = pd.DataFrame({
            "time [min]": results.t_prime,
            "temperature [K]": results.T_prime,
            "conversion": results.a_prime,
        })
        safe_mode = results.mode.lower().replace(" ", "_")
        st.download_button(
            label=_("Download Prediction Data (CSV)"),
            data=df_pred.to_csv(index=False),
            file_name=f"modelfree_prediction_{safe_mode}.csv",
            mime="text/csv",
            key=f"download_pred_mf_{safe_mode}",
        )

    def _display_modelbased_results(self, results: ModelbasedPredictionResults) -> None:
        """Render α(t) chart and CSV download for model-based isothermal prediction.

        Args:
            results: Stored model-based prediction output containing time array,
                conversion values, and the isothermal temperature used.
        """
        st.subheader(_("Model-based Isothermal Prediction — T = {iso_T:.0f} K").format(iso_T=results.iso_T))

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
            title=_("Model-based Prediction: α vs Time at T = {iso_T:.0f} K").format(iso_T=results.iso_T),
            xaxis_title=_("Time [min]"),
            yaxis_title=_("Conversion (α)"),
            yaxis_range=[0, 1.05],
            height=400,
        )
        st.plotly_chart(fig, width="stretch")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(_("Final conversion"), f"{alpha_plot[-1]:.4f}")
        with col2:
            st.metric(_("Total time predicted"), f"{results.t_pred[-1]:.2f} min")

        df_iso = pd.DataFrame({"time [min]": results.t_pred, "conversion": alpha_plot})
        st.download_button(
            label=_("Download Isothermal Prediction (CSV)"),
            data=df_iso.to_csv(index=False),
            file_name=f"isothermal_prediction_{int(results.iso_T)}K.csv",
            mime="text/csv",
            key="download_pred_mb",
        )
