"""
Activation Energy Handler Component

Manages activation energy analysis method selection and execution.
Supports five isoconversional methods: Friedman, KAS, OFW, Vyazovkin, and Advanced Vyazovkin.
"""

from typing import Optional
import streamlit as st
import numpy as np
import pandas as pd

from src.utils.SessionManager import SessionManager
from src.config import (
    SESS_BNUM,
    SESS_DATA_EXTRACTOR,
    SESS_ACTIVATION_ENERGY_OBJECT,
    SESS_ACTIVATION_ENERGY_RESULTS,
    SESS_ISOCONVERSION_RESULT,
)
from src.components.kinetics.ActivationEnergyControls import AE_METHODS
from src.models.results import ActivationEnergyResults
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
        iso_results = SessionManager.get(SESS_ISOCONVERSION_RESULT)

        if data_extractor is None or iso_results is None:
            return False

        b_num = SessionManager.get(SESS_BNUM)
        t0_num = SessionManager.get("T0num")

        try:
            ae_object = ActivationEnergy(
                Beta=b_num,
                T0=t0_num,
                IsoTables=iso_results.raw,
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
                        SessionManager.set(
                            SESS_ACTIVATION_ENERGY_RESULTS,
                            ActivationEnergyResults(
                                method=selected_method,
                                method_label=AE_METHODS[selected_method],
                                alpha=np.array(result[0]),
                                E=np.array(result[2]),
                                error=np.array(result[3]),
                                raw_result=result,
                            ),
                        )

                except Exception as e:
                    st.error(f"Error during {AE_METHODS[selected_method]} calculation: {str(e)}")

            SessionManager.set("run_ae_clicked", False)

        # Always display from session if results exist
        ae_results = SessionManager.get(SESS_ACTIVATION_ENERGY_RESULTS)
        if ae_results is not None:
            self._display_activation_energy_results(ae_results)

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

    def _display_activation_energy_results(self, ae_results: ActivationEnergyResults) -> None:
        """Display activation energy calculation results."""
        import plotly.graph_objects as go

        st.subheader(f"Activation Energy Results — {ae_results.method_label}")

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=ae_results.alpha,
                y=ae_results.E,
                mode="lines+markers",
                name=f"E ({ae_results.method})",
                error_y=dict(type="data", array=ae_results.error, visible=True),
                marker=dict(size=5),
            )
        )
        fig.update_layout(
            title=f"Activation Energy E(α) — {ae_results.method_label}",
            xaxis_title="Conversion (α)",
            yaxis_title="E [kJ/mol]",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mean E", f"{float(np.mean(ae_results.E)):.2f} kJ/mol")
        with col2:
            st.metric("Min E", f"{float(np.min(ae_results.E)):.2f} kJ/mol")
        with col3:
            st.metric("Max E", f"{float(np.max(ae_results.E)):.2f} kJ/mol")

        df_result = pd.DataFrame({
            "alpha": ae_results.alpha,
            "E [kJ/mol]": ae_results.E,
            "error [kJ/mol]": ae_results.error,
        })
        st.dataframe(df_result, use_container_width=True)

        st.download_button(
            label=f"Download {ae_results.method} Results (CSV)",
            data=df_result.to_csv(index=False),
            file_name=f"activation_energy_{ae_results.method}.csv",
            mime="text/csv",
            key=f"download_ae_{ae_results.method}",
        )

