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
from src.config import SESS_BNUM, SESS_ACTIVATION_ENERGY_OBJECT, SESS_ACTIVATION_ENERGY_RESULTS, SESS_COMP_LN_A


class ReconstructionHandler:
    """Handles the numerical reconstruction of the integral reaction model g(alpha)."""

    def render_reconstruction_controls(self) -> None:
        """Display controls for g(alpha) reconstruction."""
        st.divider()
        st.subheader("Step 8: Reaction Model Reconstruction — g(α)")

        ln_A = SessionManager.get(SESS_COMP_LN_A)
        if ln_A is None:
            st.info("Complete Step 7 (Compensation Effect) first to enable reconstruction.")
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

    def handle_reconstruction(self) -> None:
        """Execute model reconstruction and display results."""
        if not SessionManager.get("run_recon_clicked"):
            return

        activation_energy_object = SessionManager.get(SESS_ACTIVATION_ENERGY_OBJECT)
        ae_results = SessionManager.get(SESS_ACTIVATION_ENERGY_RESULTS)
        ln_A = SessionManager.get(SESS_COMP_LN_A)

        if activation_energy_object is None or ae_results is None or ln_A is None:
            st.error(
                "Missing data. Ensure activation energy and compensation effect have been computed."
            )
            return

        try:
            result = ae_results["result"]
            E = np.array(result[2])
            # reconstruction() takes A (not ln_A), so we exponentiate
            A = np.exp(ln_A)

            b_num = SessionManager.get(SESS_BNUM)
            beta_idx = SessionManager.get("recon_beta_idx", 0)
            B = float(b_num[beta_idx])

            with st.spinner("Reconstructing g(α)..."):
                g_r = activation_energy_object.reconstruction(E, A, B)

            st.success("Reaction model g(α) reconstructed successfully")

            # Store for downstream predictions
            SessionManager.set("recon_g_r", g_r)

            self._display_results(g_r, activation_energy_object)
            SessionManager.set("run_recon_clicked", False)

        except AttributeError:
            st.error(
                "Reconstruction requires accepted_models from the compensation effect step. "
                "Please re-run Step 7 before this step."
            )
            SessionManager.set("run_recon_clicked", False)
        except Exception as e:
            st.error(f"Error during reconstruction: {str(e)}")
            SessionManager.set("run_recon_clicked", False)

    def _display_results(self, g_r, activation_energy_object) -> None:
        """Display the reconstructed g(alpha) model."""
        st.subheader("Reconstructed Integral Model g(α)")

        # Align alpha values with g_r (reconstruction returns len(E)-1 points)
        alpha_full = activation_energy_object.timeAdvIsoDF.index.values
        # g_r has one fewer element than E (due to summation from i=0 to len(E)-2)
        alpha_plot = alpha_full[1 : len(g_r) + 1]
        if len(alpha_plot) > len(g_r):
            alpha_plot = alpha_plot[: len(g_r)]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=alpha_plot,
                y=g_r,
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
            yaxis_range=[0, min(2.0, float(np.max(g_r)) * 1.2)],
            xaxis_range=[0, 1],
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        df_recon = pd.DataFrame({"alpha": alpha_plot, "g_alpha": g_r})
        st.download_button(
            label="Download g(α) Data (CSV)",
            data=df_recon.to_csv(index=False),
            file_name="reaction_model_g_alpha.csv",
            mime="text/csv",
            key="download_recon",
        )
