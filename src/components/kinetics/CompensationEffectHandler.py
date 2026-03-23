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
from src.config import SESS_ACTIVATION_ENERGY_OBJECT, SESS_ACTIVATION_ENERGY_RESULTS, SESS_COMP_LN_A


class CompensationEffectHandler:
    """Handles the computation of the pre-exponential factor via the compensation effect."""

    def handle_compensation_effect(self) -> None:
        """Execute compensation effect calculation and display results."""
        if SessionManager.get("run_comp_clicked"):
            activation_energy_object = SessionManager.get(SESS_ACTIVATION_ENERGY_OBJECT)
            ae_results = SessionManager.get(SESS_ACTIVATION_ENERGY_RESULTS)

            if activation_energy_object is None or ae_results is None:
                st.error("Activation energy object or results not available.")
            else:
                try:
                    result = ae_results["result"]
                    E = np.array(result[2])
                    errorE = np.array(result[3])
                    col = SessionManager.get("comp_col", 0)

                    with st.spinner(
                        "Computing compensation effect — fitting reaction models to data..."
                    ):
                        comp_result = activation_energy_object.compensation_effect(
                            col=col, E=E, errorE=errorE
                        )

                    if comp_result is None:
                        st.error(
                            "Compensation effect could not be computed. "
                            "Try a different reference heating rate column or a different activation energy method."
                        )
                    else:
                        ln_A, errorlnA, a, errora, b, errorb, Afit, Efit, r_sq, mod = comp_result
                        st.success("Compensation effect computed successfully")
                        SessionManager.set(SESS_COMP_LN_A, ln_A)
                        SessionManager.set("comp_errorlnA", errorlnA)
                        SessionManager.set("comp_a", a)
                        SessionManager.set("comp_errora", errora)
                        SessionManager.set("comp_b", b)
                        SessionManager.set("comp_errorb", errorb)
                        SessionManager.set("comp_Afit", Afit)
                        SessionManager.set("comp_Efit", Efit)
                        SessionManager.set("comp_alpha", result[0])

                except Exception as e:
                    st.error(f"Error during compensation effect calculation: {str(e)}")

            SessionManager.set("run_comp_clicked", False)

        # Always display from session if results exist
        ln_A = SessionManager.get(SESS_COMP_LN_A)
        if ln_A is not None:
            self._display_results(
                ln_A,
                SessionManager.get("comp_errorlnA"),
                SessionManager.get("comp_a"),
                SessionManager.get("comp_errora"),
                SessionManager.get("comp_b"),
                SessionManager.get("comp_errorb"),
                SessionManager.get("comp_Afit"),
                SessionManager.get("comp_Efit"),
                SessionManager.get("comp_alpha"),
            )

    def _display_results(
        self,
        ln_A,
        errorlnA,
        a,
        errora,
        b,
        errorb,
        Afit,
        Efit,
        alpha,
    ) -> None:
        """Display compensation effect results."""
        st.subheader("Compensation Effect Results")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Slope a", f"{a:.5f}", delta=f"±{errora:.5f} (stderr)")
        with col2:
            st.metric("Intercept b", f"{b:.4f}", delta=f"±{errorb:.4f} (stderr)")
        with col3:
            st.metric("Accepted models", f"{len(Afit)}")

        st.markdown(
            f"**Compensation effect equation:** `ln(A) = {a:.4f} · E + {b:.4f}`"
        )

        # Plot 1: ln(A) vs alpha
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=alpha,
                y=ln_A,
                mode="lines+markers",
                name="ln(A)",
                error_y=dict(type="data", array=errorlnA, visible=True),
                marker=dict(size=5),
            )
        )
        fig1.update_layout(
            title="Pre-exponential Factor ln(A) vs Conversion α",
            xaxis_title="Conversion (α)",
            yaxis_title="ln(A / min⁻¹)",
            height=380,
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Plot 2: compensation effect scatter — ln(A) vs E
        if len(Efit) > 1:
            E_line = np.linspace(min(Efit) * 0.8, max(Efit) * 1.2, 100)
            lnA_line = a * E_line + b

            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(
                    x=Efit,
                    y=np.log(Afit),
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
                    name=f"ln(A) = {a:.3f}·E + {b:.3f}",
                    line=dict(dash="dash", width=2),
                )
            )
            fig2.update_layout(
                title="Compensation Effect: ln(A) vs E",
                xaxis_title="E [kJ/mol]",
                yaxis_title="ln(A / min⁻¹)",
                height=380,
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Download
        df_out = pd.DataFrame(
            {"alpha": alpha, "ln_A": ln_A, "error_ln_A": errorlnA}
        )
        st.download_button(
            label="Download ln(A) Data (CSV)",
            data=df_out.to_csv(index=False),
            file_name="compensation_effect_lnA.csv",
            mime="text/csv",
            key="download_comp_effect",
        )
