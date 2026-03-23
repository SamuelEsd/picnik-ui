"""
Activation Energy Handler Component

Manages activation energy analysis method selection and execution.
Supports five isoconversional methods: Friedman, KAS, OFW, Vyazovkin, and Advanced Vyazovkin.
"""

from typing import Optional
import streamlit as st
import pandas as pd

from src.utils.SessionManager import SessionManager
from src.config import SESS_BNUM, SESS_DATA_EXTRACTOR, SESS_ACTIVATION_ENERGY_OBJECT, SESS_ACTIVATION_ENERGY_RESULTS
from src.components.kinetics.ActivationEnergyControls import AE_METHODS
from picnick_dev import ActivationEnergy


class ActivationEnergyHandler:
    """Executes activation energy calculations and displays results."""

    def setup(self) -> bool:
        """
        Build and store the ActivationEnergy object from session prerequisites.

        Returns True if the object was created successfully, False otherwise.
        Silently returns False when isoconversion has not been run yet.
        """
        data_extractor = SessionManager.get(SESS_DATA_EXTRACTOR)
        isoconversion_results = SessionManager.get("isoconversion_results")

        if data_extractor is None or isoconversion_results is None:
            return False

        b_num = SessionManager.get(SESS_BNUM)
        t0_num = SessionManager.get("T0num")

        try:
            ae_object = ActivationEnergy(
                Beta=b_num,
                T0=t0_num,
                IsoTables=isoconversion_results,
            )
            SessionManager.set(SESS_ACTIVATION_ENERGY_OBJECT, ae_object)
            return True
        except Exception as e:
            st.error(f"Error creating Activation Energy object: {str(e)}")
            return False

    def handle_activation_energy(self) -> None:
        """Execute activation energy calculation using the selected method."""
        if SessionManager.get("run_ae_clicked"):
            activation_energy_object = SessionManager.get(SESS_ACTIVATION_ENERGY_OBJECT)
            selected_method = SessionManager.get("selected_ae_method", "Fr")

            if activation_energy_object is None:
                st.error("No Activation Energy object available for calculation.")
            else:
                try:
                    with st.spinner(f"Running {AE_METHODS[selected_method]} calculation..."):
                        result = self._execute_method(activation_energy_object, selected_method)

                    if result is None:
                        st.error(f"{AE_METHODS[selected_method]} calculation failed.")
                    else:
                        st.success(f"{AE_METHODS[selected_method]} calculation completed successfully")
                        SessionManager.set(SESS_ACTIVATION_ENERGY_RESULTS, {
                            "method": selected_method,
                            "method_label": AE_METHODS[selected_method],
                            "result": result,
                        })

                except Exception as e:
                    st.error(f"Error during {AE_METHODS[selected_method]} calculation: {str(e)}")

            SessionManager.set("run_ae_clicked", False)

        # Always display from session if results exist
        ae_results = SessionManager.get(SESS_ACTIVATION_ENERGY_RESULTS)
        if ae_results is not None:
            self._display_activation_energy_results(ae_results["result"], ae_results["method"])

    def _execute_method(
        self, activation_energy_object: ActivationEnergy, method: str
    ) -> Optional[pd.DataFrame]:
        """
        Execute the selected activation energy method.

        Args:
            activation_energy_object: ActivationEnergy instance.
            method: Method to execute ('Fr', 'KAS', 'OFW', 'Vy', or 'aVy').

        Returns:
            Result DataFrame or None on error.
        """
        try:
            if method == "Fr":
                result = activation_energy_object.Fr()
            elif method == "KAS":
                result = activation_energy_object.KAS()
            elif method == "OFW":
                result = activation_energy_object.OFW()
            elif method == "Vy":
                result = activation_energy_object.Vy(bounds=(1, 300))
            elif method == "aVy":
                p_value = SessionManager.get("avy_p_value", 0.50)
                result = activation_energy_object.aVy(bounds=(1, 300), p=p_value)
            else:
                st.error(f"Unknown method: {method}")
                return None

            return result
        except Exception as e:
            st.error(f"Method execution failed: {str(e)}")
            return None

    def _display_activation_energy_results(
        self, result, method: str
    ) -> None:
        """
        Display activation energy calculation results.

        Args:
            result: Tuple (alpha, T_avg, E, error, ...) returned by each method.
            method: Method used for calculation.
        """
        st.subheader(f"Activation Energy Results — {AE_METHODS[method]}")

        # All methods return a tuple: (alpha, T_avg, E, error, ...)
        try:
            import numpy as np
            import plotly.graph_objects as go

            alpha_vals = result[0]
            E_vals = result[2]
            error_vals = result[3]

            # Interactive E(alpha) chart with error bars
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=alpha_vals,
                    y=E_vals,
                    mode="lines+markers",
                    name=f"E ({method})",
                    error_y=dict(type="data", array=error_vals, visible=True),
                    marker=dict(size=5),
                )
            )
            fig.update_layout(
                title=f"Activation Energy E(α) — {AE_METHODS[method]}",
                xaxis_title="Conversion (α)",
                yaxis_title="E [kJ/mol]",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mean E", f"{float(np.mean(E_vals)):.2f} kJ/mol")
            with col2:
                st.metric("Min E", f"{float(np.min(E_vals)):.2f} kJ/mol")
            with col3:
                st.metric("Max E", f"{float(np.max(E_vals)):.2f} kJ/mol")

            # DataFrame display
            df_result = pd.DataFrame(
                {"alpha": alpha_vals, "E [kJ/mol]": E_vals, "error [kJ/mol]": error_vals}
            )
            st.dataframe(df_result, use_container_width=True)
            csv_data = df_result.to_csv(index=False)

        except (TypeError, IndexError, Exception):
            # Fallback for unexpected result formats
            st.write(result)
            csv_data = str(result)

        # Download button for results
        st.download_button(
            label=f"Download {method} Results (CSV)",
            data=csv_data,
            file_name=f"activation_energy_{method}.csv",
            mime="text/csv",
            key=f"download_ae_{method}",
        )

