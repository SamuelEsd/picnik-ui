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


class CompensationEffectHandler:
    """Handles the computation of the pre-exponential factor via the compensation effect."""

    def render_compensation_controls(self) -> None:
        """Display controls for compensation effect calculation."""
        st.divider()
        st.subheader("Step 7: Pre-exponential Factor — Compensation Effect")

        ae_results = SessionManager.get("activation_energy_results")
        if ae_results is None:
            st.info("Complete Step 6 (Activation Energy) first to enable this step.")
            return

        b_num = SessionManager.get("Bnum")
        if b_num is None:
            st.info("Heating rate data not available.")
            return

        col1, col2 = st.columns([3, 1])

        with col1:
            beta_options = {
                i: f"β = {b:.2f} K/min (column {i})"
                for i, b in enumerate(b_num)
            }
            selected_col = st.selectbox(
                "Reference heating rate for model fitting",
                options=list(beta_options.keys()),
                format_func=lambda x: beta_options[x],
                help=(
                    "The compensation effect fits reaction models to data at this heating rate. "
                    "The last (highest) heating rate often gives the best signal."
                ),
                key="comp_col_selector",
            )
            SessionManager.set("comp_col", selected_col)

        with col2:
            st.write("")
            st.write("")
            if st.button(
                "Calculate Compensation Effect",
                type="primary",
                key="comp_calc_btn",
            ):
                SessionManager.set("run_comp_clicked", True)

    def handle_compensation_effect(self) -> None:
        """Execute compensation effect calculation and display results."""
        if not SessionManager.get("run_comp_clicked"):
            return

        activation_energy_object = SessionManager.get("activation_energy_object")
        ae_results = SessionManager.get("activation_energy_results")

        if activation_energy_object is None or ae_results is None:
            st.error("Activation energy object or results not available.")
            return

        try:
            result = ae_results["result"]
            # All methods return (alpha, T_avg, E, error, ...) as a tuple
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
                SessionManager.set("run_comp_clicked", False)
                return

            ln_A, errorlnA, a, errora, b, errorb, Afit, Efit, r_sq, mod = comp_result

            st.success("Compensation effect computed successfully")

            # Store results in session for downstream use (reconstruction, predictions)
            SessionManager.set("comp_ln_A", ln_A)
            SessionManager.set("comp_errorlnA", errorlnA)
            SessionManager.set("comp_a", a)
            SessionManager.set("comp_b", b)
            SessionManager.set("comp_Afit", Afit)
            SessionManager.set("comp_Efit", Efit)
            SessionManager.set("comp_alpha", result[0])  # alpha values

            self._display_results(
                ln_A, errorlnA, a, errora, b, errorb, Afit, Efit, result[0]
            )
            SessionManager.set("run_comp_clicked", False)

        except Exception as e:
            st.error(f"Error during compensation effect calculation: {str(e)}")
            SessionManager.set("run_comp_clicked", False)

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
