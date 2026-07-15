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
import plotly.express as px

from src.i18n import _
from src.utils.SessionManager import SessionManager
from src.config import SESS_ACTIVATION_ENERGY_OBJECT, SESS_ACTIVATION_ENERGY_RESULTS, SESS_COMP_RESULTS, SESS_RUN_COMP, SESS_COMP_COL, SESS_COMP_ERROR_M
from src.models.results import CompensationEffectResults


class CompensationEffectHandler:
    """Handles the computation of the pre-exponential factor via the compensation effect."""

    def handle_compensation_effect(self) -> None:
        """Compute the pre-exponential factor A(α) via the compensation effect.

        Reads SESS_RUN_COMP. When True, calls ActivationEnergy.compensation_effect()
        using E(α) from the active method and the configured error metric (mse_NL,
        r_NL, or r_Lin). Stores a CompensationEffectResults in session state and
        invalidates reconstruction and prediction results. Always renders stored
        results at the end of the call.
        """
        if st.session_state.get(SESS_RUN_COMP):
            activation_energy_object = st.session_state.get(SESS_ACTIVATION_ENERGY_OBJECT)
            ae_results = SessionManager.get_active_ae_result()

            if activation_energy_object is None or ae_results is None:
                st.error(_("Activation energy object or results not available."))
            else:
                SessionManager.clear_downstream_from("compensation")
                try:
                    E = ae_results.E
                    errorE = ae_results.error
                    col = st.session_state.get(SESS_COMP_COL, 0)
                    error_m = st.session_state.get(SESS_COMP_ERROR_M, 'mse_NL')

                    with st.spinner(
                        _("Computing compensation effect — fitting reaction models to data...")
                    ):
                        comp_result = activation_energy_object.compensation_effect(
                            col=col, E=E, errorE=errorE, error_m=error_m
                        )

                    if comp_result is None:
                        st.error(
                            _(
                                "Compensation effect could not be computed. "
                                "Try a different reference heating rate column or a different activation energy method."
                            )
                        )
                    else:
                        ln_A, errorlnA, a, errora, b, errorb, Afit, Efit, r_sq, mod = comp_result
                        st.success(_("Compensation effect computed successfully"))
                        st.session_state[SESS_COMP_RESULTS] = CompensationEffectResults(
                                alpha=ae_results.alpha,
                                ln_A=ln_A,
                                error_ln_A=errorlnA,
                                a=a,
                                error_a=errora,
                                b=b,
                                error_b=errorb,
                                A_fit=Afit,
                                E_fit=Efit,
                                accepted_models=list(mod) if mod is not None else [],
                            )

                except Exception as e:
                    st.error(_("Error during compensation effect calculation: {error}").format(error=str(e)))

            st.session_state[SESS_RUN_COMP] = False

        # Always display from session if results exist
        comp_results = st.session_state.get(SESS_COMP_RESULTS)
        if comp_results is not None:
            self._display_results(comp_results)

    def _display_results(self, results: CompensationEffectResults) -> None:
        """Render ln(A) vs α chart, compensation scatter plot, and accepted-models list.

        Args:
            results: Stored compensation effect output containing ln(A), fit
                parameters a and b, and the list of accepted reaction models.
        """
        st.subheader(_("Compensation Effect Results"))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(_("Slope a"), f"{results.a:.5f}", delta=_("±{value:.5f} (stderr)").format(value=results.error_a))
        with col2:
            st.metric(_("Intercept b"), f"{results.b:.4f}", delta=_("±{value:.4f} (stderr)").format(value=results.error_b))
        with col3:
            st.metric(_("Accepted models"), f"{len(results.A_fit)}")

        st.markdown(
            _("**Compensation effect equation:** `ln(A) = {a:.4f} · E + {b:.4f}`").format(a=results.a, b=results.b)
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
            title=_("Pre-exponential Factor ln(A) vs Conversion α"),
            xaxis_title=_("Conversion (α)"),
            yaxis_title=_("ln(A / min⁻¹)"),
            height=380,
        )
        st.plotly_chart(fig1, width="stretch")

        with st.expander(_("ln(A) statistics")):
            lnA = results.ln_A
            st.write(_("**Mean:** {value:.4f}").format(value=float(np.mean(lnA))))
            st.write(_("**Min:** {value:.4f}  (α = {alpha:.3f})").format(
                value=float(np.min(lnA)), alpha=float(results.alpha[int(np.argmin(lnA))])
            ))
            st.write(_("**Max:** {value:.4f}  (α = {alpha:.3f})").format(
                value=float(np.max(lnA)), alpha=float(results.alpha[int(np.argmax(lnA))])
            ))

        # Plot 2: compensation effect scatter — ln(A) vs E, one trace per model
        # so each point can be identified by its reaction model name.
        model_names = [getattr(m, "__name__", str(m)) for m in results.accepted_models]

        if len(results.E_fit) > 1:
            E_line = np.linspace(min(results.E_fit) * 0.8, max(results.E_fit) * 1.2, 100)
            lnA_line = results.a * E_line + results.b

            fig2 = go.Figure()
            palette = px.colors.qualitative.Plotly
            for i in range(len(results.E_fit)):
                name = model_names[i] if i < len(model_names) else f"model_{i}"
                color = palette[i % len(palette)]
                fig2.add_trace(
                    go.Scatter(
                        x=[results.E_fit[i]],
                        y=[np.log(results.A_fit[i])],
                        mode="markers+text",
                        name=name,
                        text=[name],
                        textposition="top center",
                        textfont=dict(size=10, color=color),
                        marker=dict(size=9, symbol="circle", color=color),
                        hovertemplate=f"{name}<br>E=%{{x:.2f}} kJ/mol<br>ln(A)=%{{y:.3f}}<extra></extra>",
                    )
                )
            fig2.add_trace(
                go.Scatter(
                    x=E_line,
                    y=lnA_line,
                    mode="lines",
                    name=f"ln(A) = {results.a:.3f}·E + {results.b:.3f}",
                    line=dict(dash="dash", width=2, color="#333333"),
                )
            )
            fig2.update_layout(
                title=_("Compensation Effect: ln(A) vs E (by reaction model)"),
                xaxis_title=_("E [kJ/mol]"),
                yaxis_title=_("ln(A / min⁻¹)"),
                height=380,
            )
            st.plotly_chart(fig2, width="stretch")

        if results.accepted_models:
            st.markdown(_("**Accepted models ({n}):** {names}").format(
                n=len(results.accepted_models), names=", ".join(model_names)
            ))

        df_out = pd.DataFrame({
            "alpha": results.alpha,
            "ln_A": results.ln_A,
            "error_ln_A": results.error_ln_A,
        })
        st.download_button(
            label=_("Download ln(A) Data (CSV)"),
            data=df_out.to_csv(index=False),
            file_name="compensation_effect_lnA.csv",
            mime="text/csv",
            key="download_comp_effect",
        )
