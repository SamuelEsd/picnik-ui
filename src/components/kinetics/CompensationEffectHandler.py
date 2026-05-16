"""
Compensation Effect Handler Component

Computes the pre-exponential factor A(alpha) via the compensation effect:
    ln(A) = a + b*E

This is Step 7 in the pICNIK workflow, coming after activation energy calculation.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.utils.SessionManager import SessionManager
from src.config import SESS_ACTIVATION_ENERGY_OBJECT, SESS_ACTIVATION_ENERGY_RESULTS, SESS_COMP_RESULTS, SESS_RUN_COMP, SESS_COMP_COL, SESS_COMP_ERROR_M
from src.models.results import CompensationEffectResults
from src.components.kinetics.ActivationEnergyHandler import get_active_ae_result


class CompensationEffectHandler:
    """Handles the computation of the pre-exponential factor via the compensation effect."""

    def handle_compensation_effect(self) -> None:
        """Execute compensation effect calculation and display results."""
        if SessionManager.get(SESS_RUN_COMP):
            activation_energy_object = SessionManager.get(SESS_ACTIVATION_ENERGY_OBJECT)
            ae_results = get_active_ae_result()

            if activation_energy_object is None or ae_results is None:
                st.error("Activation energy object or results not available.")
            else:
                try:
                    E = ae_results.E
                    errorE = ae_results.error
                    col = SessionManager.get(SESS_COMP_COL, 0)
                    error_m = SessionManager.get(SESS_COMP_ERROR_M, 'mse_NL')

                    with st.spinner(
                        "Computing compensation effect — fitting reaction models to data..."
                    ):
                        comp_result = activation_energy_object.compensation_effect(
                            col=col, E=E, errorE=errorE, error_m=error_m
                        )

                    if comp_result is None:
                        st.error(
                            "Compensation effect could not be computed. "
                            "Try a different reference heating rate column or a different activation energy method."
                        )
                    else:
                        ln_A, errorlnA, a, errora, b, errorb, Afit, Efit, r_sq, mod = comp_result
                        st.success("Compensation effect computed successfully")
                        SessionManager.set(
                            SESS_COMP_RESULTS,
                            CompensationEffectResults(
                                alpha=ae_results.alpha,
                                ln_A=ln_A,
                                error_ln_A=errorlnA,
                                a=a,
                                error_a=errora,
                                b=b,
                                error_b=errorb,
                                A_fit=Afit,
                                E_fit=Efit,
                            ),
                        )

                except Exception as e:
                    st.error(f"Error during compensation effect calculation: {str(e)}")

            SessionManager.set(SESS_RUN_COMP, False)

        # Always display from session if results exist
        comp_results = SessionManager.get(SESS_COMP_RESULTS)
        if comp_results is not None:
            self._display_results(comp_results)

    def _display_results(self, results: CompensationEffectResults) -> None:
        """Display compensation effect results."""
        st.subheader("Compensation Effect Results")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Slope a", f"{results.a:.5f}", delta=f"±{results.error_a:.5f} (stderr)")
        with col2:
            st.metric("Intercept b", f"{results.b:.4f}", delta=f"±{results.error_b:.4f} (stderr)")
        with col3:
            st.metric("Accepted models", f"{len(results.A_fit)}")

        st.markdown(
            f"**Compensation effect equation:** `ln(A) = {results.a:.4f} · E + {results.b:.4f}`"
        )

        # Plot 1: ln(A) vs alpha
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=results.alpha,
                y=results.ln_A,
                mode="lines+markers",
                name="ln(A)",
                error_y=dict(type="data", array=results.error_ln_A, visible=True),
                marker=dict(size=5),
            )
        )
        fig1.update_layout(
            title="Pre-exponential Factor ln(A) vs Conversion α",
            xaxis_title="Conversion (α)",
            yaxis_title="ln(A / min⁻¹)",
            height=380,
        )
        st.plotly_chart(fig1, width="stretch")

        # Plot 2: compensation effect scatter — ln(A) vs E
        if len(results.E_fit) > 1:
            E_line = np.linspace(min(results.E_fit) * 0.8, max(results.E_fit) * 1.2, 100)
            lnA_line = results.a * E_line + results.b

            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(
                    x=results.E_fit,
                    y=np.log(results.A_fit),
                    mode="markers",
                    name="Model fits (Eᵢ, ln Aᵢ)",
                    marker=dict(size=9, symbol="circle"),
                )
            )
            fig2.add_trace(
                go.Scatter(
                    x=E_line,
                    y=lnA_line,
                    mode="lines",
                    name=f"ln(A) = {results.a:.3f}·E + {results.b:.3f}",
                    line=dict(dash="dash", width=2),
                )
            )
            fig2.update_layout(
                title="Compensation Effect: ln(A) vs E",
                xaxis_title="E [kJ/mol]",
                yaxis_title="ln(A / min⁻¹)",
                height=380,
            )
            st.plotly_chart(fig2, width="stretch")

        df_out = pd.DataFrame({
            "alpha": results.alpha,
            "ln_A": results.ln_A,
            "error_ln_A": results.error_ln_A,
        })
        st.download_button(
            label="Download ln(A) Data (CSV)",
            data=df_out.to_csv(index=False),
            file_name="compensation_effect_lnA.csv",
            mime="text/csv",
            key="download_comp_effect",
        )
