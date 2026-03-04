"""
Activation Energy Handler Component

Manages activation energy analysis method selection and execution.
Supports five isoconversional methods: Friedman, KAS, OFW, Vyazovkin, and Advanced Vyazovkin.
"""

from typing import Optional
import streamlit as st
import pandas as pd

from src.utils.SessionManager import SessionManager
from picnick_dev import ActivationEnergy


class ActivationEnergyHandler:
    """Component for handling activation energy analysis method selection and execution."""

    # Method definitions with values and labels
    METHODS = {
        "Fr": "Friedman method",
        "KAS": "Kissinger-Akahira-Sunose method",
        "OFW": "Osawa-Flynn-Wall method",
        "Vy": "Vyazovkin method",
        "aVy": "Advanced Vyazovkin method",
    }

    def render_activation_energy_controls(self) -> None:
        """Display activation energy method selection controls."""
        st.divider()
        st.subheader("Activation Energy Analysis")

        # Display instruction text
        st.write("**Choose the method to use for activation energy calculation:**")

        col1, col2 = st.columns([3, 1])

        with col1:
            selected_method = st.selectbox(
                "Select Activation Energy Method",
                options=list(self.METHODS.keys()),
                format_func=lambda x: self.METHODS[x],
                help="Select one of the five available isoconversional methods for activation energy calculation",
                key="ae_method_selectbox",
            )
            SessionManager.set("selected_ae_method", selected_method)

        with col2:
            st.write("")
            st.write("")
            if st.button(
                "Calculate Activation Energy",
                type="primary",
                key="ae_calculate_btn",
            ):
                SessionManager.set("run_ae_clicked", True)

    def handle_activation_energy(self) -> None:
        """Execute activation energy calculation using the selected method."""
        if not SessionManager.get("run_ae_clicked"):
            return

        activation_energy_object = SessionManager.get("activation_energy_object")
        selected_method = SessionManager.get("selected_ae_method", "Fr")

        if activation_energy_object is None:
            st.error("No Activation Energy object available for calculation.")
            return

        try:
            st.info(
                f"Running {self.METHODS[selected_method]} calculation..."
            )

            # Execute the selected method
            result = self._execute_method(activation_energy_object, selected_method)

            if result is None:
                st.error(
                    f"{self.METHODS[selected_method]} calculation failed."
                )
                return

            st.success(
                f"{self.METHODS[selected_method]} calculation completed successfully"
            )

            # Display results
            self._display_activation_energy_results(result, selected_method)

            # Clear the button state
            SessionManager.set("run_ae_clicked", False)

        except Exception as e:
            st.error(
                f"Error during {self.METHODS[selected_method]} calculation: {str(e)}"
            )

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
                result = activation_energy_object.aVy(bounds=(1, 300))
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
            result: Calculation result (typically DataFrame or array).
            method: Method used for calculation.
        """
        st.subheader(f"Activation Energy Results - {self.METHODS[method]}")

        # Display the result
        if isinstance(result, pd.DataFrame):
            st.dataframe(result, width='stretch')
            csv_data = result.to_csv(index=True)
        else:
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

        # Store results in session for later use
        SessionManager.set("activation_energy_results", {
            "method": method,
            "method_label": self.METHODS[method],
            "result": result,
        })
