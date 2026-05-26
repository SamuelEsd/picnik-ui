"""
Reconstruction Handler Component

Numerically reconstructs the integral reaction model g(alpha) using:
    g(alpha) = sum_i A_i * J(E_i, t_i)

This is Step 8 in the pICNIK workflow. Requires compensation effect (Step 7) first
because it uses the accepted_models list set internally during compensation_effect().
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
    SESS_RUN_RECON,
    SESS_RECON_BETA_IDX,
)
from src.models.results import ReconstructionResults


class ReconstructionHandler:
    """Handles the numerical reconstruction of the integral reaction model g(alpha)."""

    def handle_reconstruction(self) -> None:
        """Numerically reconstruct the integral reaction model g(α).

        Reads SESS_RUN_RECON. When True, calls ActivationEnergy.reconstruction()
        using E(α) from the active method, A(α) from the compensation effect step,
        and the user-selected reference heating rate β. Stores a ReconstructionResults
        in session state and invalidates prediction results. Always renders the
        stored g(α) chart at the end of the call.
        """
        if st.session_state.get(SESS_RUN_RECON):
            activation_energy_object = st.session_state.get(SESS_ACTIVATION_ENERGY_OBJECT)
            ae_results = SessionManager.get_active_ae_result()
            comp_results = st.session_state.get(SESS_COMP_RESULTS)

            if activation_energy_object is None or ae_results is None or comp_results is None:
                st.error(
                    "Missing data. Ensure activation energy and compensation effect have been computed."
                )
            else:
                SessionManager.clear_downstream_from("reconstruction")
                try:
                    E = ae_results.E
                    A = np.exp(comp_results.ln_A)

                    b_num = st.session_state.get(SESS_BNUM)
                    beta_idx = st.session_state.get(SESS_RECON_BETA_IDX, 0)
                    B = float(b_num[beta_idx])

                    with st.spinner("Reconstructing g(α)..."):
                        g_r = activation_energy_object.reconstruction(E, A, B)

                    st.success("Reaction model g(α) reconstructed successfully")

                    alpha_full = activation_energy_object.timeAdvIsoDF.index.values
                    alpha_plot = alpha_full[1: len(g_r) + 1]
                    if len(alpha_plot) > len(g_r):
                        alpha_plot = alpha_plot[: len(g_r)]

                    st.session_state[SESS_RECON_RESULTS] = ReconstructionResults(g_r=g_r, alpha_plot=alpha_plot)

                except AttributeError:
                    st.error(
                        "Reconstruction requires accepted_models from the compensation effect step. "
                        "Please re-run Step 8 before this step."
                    )
                except Exception as e:
                    st.error(f"Error during reconstruction: {str(e)}")

            st.session_state[SESS_RUN_RECON] = False

        # Always display from session if results exist
        recon_results = st.session_state.get(SESS_RECON_RESULTS)
        if recon_results is not None:
            self._display_results(recon_results)

    def _display_results(self, results: ReconstructionResults) -> None:
        """Render the reconstructed g(α) curve and CSV download button.

        Args:
            results: Stored reconstruction output containing the g_r array
                and the corresponding alpha_plot values.
        """
        st.subheader("Reconstructed Integral Model g(α)")

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=results.alpha_plot,
                y=results.g_r,
                mode="lines+markers",
                name="g(α) reconstructed",
                marker=dict(size=4, symbol="star"),
                line=dict(width=2, color="#6963DB"),
            )
        )
        fig.update_layout(
            title="Numerically Reconstructed Integral Model g(α)",
            xaxis_title="Conversion (α)",
            yaxis_title="g(α)",
            yaxis_range=[0, min(2.0, float(np.max(results.g_r)) * 1.2)],
            xaxis_range=[0, 1],
            height=400,
        )
        st.plotly_chart(fig, width="stretch")

        df_recon = pd.DataFrame({"alpha": results.alpha_plot, "g_alpha": results.g_r})
        st.download_button(
            label="Download g(α) Data (CSV)",
            data=df_recon.to_csv(index=False),
            file_name="reaction_model_g_alpha.csv",
            mime="text/csv",
            key="download_recon",
        )
