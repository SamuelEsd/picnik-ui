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

            # Display P parameter input for aVy method, inside col1
            if selected_method == "aVy":
                p_value = st.slider(
                    "P value (Advanced Vyazovkin)",
                    min_value=0.50,
                    max_value=0.99,
                    step=0.01,
                    value=SessionManager.get("avy_p_value", 0.50),
                    help="Set the P parameter for Advanced Vyazovkin method (0.50 to 0.99)",
                    key="avy_p_slider",
                )
                SessionManager.set("avy_p_value", p_value)

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
            with st.spinner(f"Running {self.METHODS[selected_method]} calculation..."):
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
        st.subheader(f"Activation Energy Results — {self.METHODS[method]}")

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
                title=f"Activation Energy E(α) — {self.METHODS[method]}",
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

        # Store results in session for later use (compensation effect, predictions)
        SessionManager.set("activation_energy_results", {
            "method": method,
            "method_label": self.METHODS[method],
            "result": result,
        })
