"""
Activation Energy Handler Component

Manages activation energy analysis: runs all user-selected isoconversional methods,
stores results as a dict keyed by method name, and displays them in a combined chart.
"""

from typing import Optional
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.utils.SessionManager import SessionManager
from src.config import (
    SESS_BNUM,
    SESS_T0_NUM,
    SESS_DATA_EXTRACTOR,
    SESS_ACTIVATION_ENERGY_OBJECT,
    SESS_ACTIVATION_ENERGY_RESULTS,
    SESS_ISOCONVERSION_RESULT,
    SESS_RUN_AE,
    SESS_AE_METHODS,
    SESS_AE_ACTIVE_METHOD,
    SESS_AE_SHOW_ERROR,
    SESS_AVY_P_VALUE,
    SESS_VY_BOUNDS,
)
from src.components.kinetics.ActivationEnergyControls import AE_METHODS, AE_METHOD_COLORS
from src.models.results import ActivationEnergyResults
from picnick_dev import ActivationEnergy


class ActivationEnergyHandler:
    """Executes activation energy calculations and displays combined results."""

    def setup(self) -> bool:
        """Build and cache the ActivationEnergy pICNIK object in session state.

        Instantiates ActivationEnergy from the stored DataExtraction object and
        isoconversion tables. The object is created only once per session to
        preserve stateful attributes (e.g. accepted_models) written by the
        compensation effect step. Must be called before handle_activation_energy().

        Returns:
            True if the ActivationEnergy object is available (created or cached),
            False if prerequisites are missing or instantiation fails.
        """
        data_extractor = st.session_state.get(SESS_DATA_EXTRACTOR)
        iso_results = st.session_state.get(SESS_ISOCONVERSION_RESULT)

        if data_extractor is None or iso_results is None:
            return False

        if st.session_state.get(SESS_ACTIVATION_ENERGY_OBJECT) is not None:
            return True

        b_num = st.session_state.get(SESS_BNUM)
        t0_num = st.session_state.get(SESS_T0_NUM)

        try:
            ae_object = ActivationEnergy(
                Beta=b_num,
                T0=t0_num,
                IsoTables=iso_results.raw,
            )
            st.session_state[SESS_ACTIVATION_ENERGY_OBJECT] = ae_object
            return True
        except Exception as e:
            st.error(f"Error creating Activation Energy object: {str(e)}")
            return False

    def handle_activation_energy(self) -> None:
        """Run all user-selected isoconversional methods and display the combined chart.

        Reads SESS_RUN_AE and SESS_AE_METHODS. For each selected method, calls
        _execute_method(), wraps the result in an ActivationEnergyResults dataclass,
        and accumulates them in a dict keyed by method name stored under
        SESS_ACTIVATION_ENERGY_RESULTS. Downstream steps (compensation through
        predictions) are invalidated before the new results are stored.
        Always renders the combined E(α) chart from session at the end of the call.
        """
        if st.session_state.get(SESS_RUN_AE):
            activation_energy_object = st.session_state.get(SESS_ACTIVATION_ENERGY_OBJECT)
            selected_methods = st.session_state.get(SESS_AE_METHODS, [])

            if activation_energy_object is None:
                st.error("No Activation Energy object available for calculation.")
            elif not selected_methods:
                st.warning("No methods selected.")
            else:
                SessionManager.clear_downstream_from("activation_energy")
                # Preserve any previously computed results and add/overwrite with new ones.
                existing = st.session_state.get(SESS_ACTIVATION_ENERGY_RESULTS)
                results_dict: dict[str, ActivationEnergyResults] = (
                    existing if isinstance(existing, dict) else {}
                )

                for method in selected_methods:
                    with st.spinner(f"Running {AE_METHODS[method]}..."):
                        result = self._execute_method(activation_energy_object, method)

                    if result is None:
                        st.error(f"{AE_METHODS[method]} calculation failed.")
                    else:
                        alpha, E, error = self._parse_result(result, method)
                        results_dict[method] = ActivationEnergyResults(
                            method=method,
                            method_label=AE_METHODS[method],
                            alpha=alpha,
                            E=E,
                            error=error,
                            raw_result=result,
                        )
                        st.success(f"{AE_METHODS[method]} completed")

                if results_dict:
                    st.session_state[SESS_ACTIVATION_ENERGY_RESULTS] = results_dict
                    # Default active method to the best one computed
                    current_active = st.session_state.get(SESS_AE_ACTIVE_METHOD)
                    if current_active not in results_dict:
                        for m in ("aVy", "Vy", "KAS", "OFW", "Fr"):
                            if m in results_dict:
                                st.session_state[SESS_AE_ACTIVE_METHOD] = m
                                break

            st.session_state[SESS_RUN_AE] = False

        # Always display from session if results exist
        results = st.session_state.get(SESS_ACTIVATION_ENERGY_RESULTS)
        if results is not None:
            results_dict = results if isinstance(results, dict) else {}
            if results_dict:
                self._display_results(results_dict)

    def _execute_method(
        self, ae_object: ActivationEnergy, method: str
    ) -> Optional[object]:
        """Call the corresponding pICNIK method on the ActivationEnergy object.

        Args:
            ae_object: Instantiated pICNIK ActivationEnergy object.
            method: Method key — one of 'Fr', 'OFW', 'KAS', 'Vy', 'aVy'.

        Returns:
            Raw tuple returned by the pICNIK method, or None if execution fails.
        """
        try:
            if method == "Fr":
                return ae_object.Fr()
            elif method == "KAS":
                return ae_object.KAS()
            elif method == "OFW":
                return ae_object.OFW()
            elif method == "Vy":
                bounds = st.session_state.get(SESS_VY_BOUNDS, (1.0, 300.0))
                return ae_object.Vy(bounds=bounds)
            elif method == "aVy":
                bounds = st.session_state.get(SESS_VY_BOUNDS, (1.0, 300.0))
                p_value = st.session_state.get(SESS_AVY_P_VALUE, 0.50)
                return ae_object.aVy(bounds=bounds, p=p_value)
            else:
                st.error(f"Unknown method: {method}")
                return None
        except Exception as e:
            st.error(f"{method} execution failed: {str(e)}")
            return None

    def _parse_result(
        self, result: object, method: str
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Extract (alpha, E, error) arrays from a raw pICNIK method result.

        All pICNIK methods return a sequence whose first four elements are:
        [0] alpha — conversion values, [1] T_mean — not used here,
        [2] E — activation energies in kJ/mol, [3] error — uncertainty at 95%.

        Args:
            result: Raw return value from any pICNIK isoconversional method.
            method: Method key (used only for potential future dispatch).

        Returns:
            Tuple of (alpha, E, error) as NumPy arrays.
        """
        result = tuple(result)
        alpha = np.array(result[0])
        E     = np.array(result[2])
        error = np.array(result[3])
        return alpha, E, error

    def _display_results(self, results_dict: dict[str, ActivationEnergyResults]) -> None:
        """Render the combined E(α) chart, active-method selector, and per-method downloads.

        Args:
            results_dict: Mapping of method key → ActivationEnergyResults for every
                method that has been computed in the current session.
        """
        st.subheader("Activation Energy Results — E(α)")

        show_error = st.session_state.get(SESS_AE_SHOW_ERROR, True)

        fig = go.Figure()
        for method, res in results_dict.items():
            color = AE_METHOD_COLORS.get(method, "#888888")
            has_error = show_error and bool(np.any(res.error != 0))
            fig.add_trace(
                go.Scatter(
                    x=res.alpha,
                    y=res.E,
                    mode="lines+markers",
                    name=res.method_label,
                    marker=dict(size=5, color=color),
                    line=dict(color=color),
                    error_y=dict(
                        type="data",
                        array=res.error,
                        visible=has_error,
                        color=color,
                        thickness=1.2,
                    ),
                )
            )

        fig.update_layout(
            xaxis_title="Conversion (α)",
            yaxis_title="E [kJ/mol]",
            height=440,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Active method selector — drives downstream steps
        active_method = st.session_state.get(SESS_AE_ACTIVE_METHOD)
        if active_method not in results_dict:
            active_method = next(iter(results_dict))

        new_active = st.selectbox(
            "Use for downstream steps (Compensation Effect, Reconstruction, Prediction):",
            options=list(results_dict.keys()),
            format_func=lambda k: AE_METHODS[k],
            index=list(results_dict.keys()).index(active_method),
            key="ae_active_method_selector",
            help=(
                "The E(α) from this method will be passed to Steps 8–10. "
                "aVy is the most rigorous choice when methods disagree."
            ),
        )
        st.session_state[SESS_AE_ACTIVE_METHOD] = new_active

        # Per-method metrics and download buttons
        with st.expander("Method details & downloads", expanded=False):
            for method, res in results_dict.items():
                color = AE_METHOD_COLORS.get(method, "#888888")
                st.markdown(
                    f'<span style="display:inline-block;width:12px;height:12px;'
                    f'border-radius:2px;background:{color};margin-right:6px"></span>'
                    f"**{res.method_label}**",
                    unsafe_allow_html=True,
                )
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    st.metric("Mean E", f"{float(np.mean(res.E)):.2f} kJ/mol")
                with mc2:
                    st.metric("Min E", f"{float(np.min(res.E)):.2f} kJ/mol")
                with mc3:
                    st.metric("Max E", f"{float(np.max(res.E)):.2f} kJ/mol")

                df = pd.DataFrame({
                    "alpha": res.alpha,
                    "E [kJ/mol]": res.E,
                    "error [kJ/mol]": res.error,
                })
                st.download_button(
                    label=f"Download {method} results (CSV)",
                    data=df.to_csv(index=False),
                    file_name=f"activation_energy_{method}.csv",
                    mime="text/csv",
                    key=f"download_ae_{method}",
                )
                st.divider()
