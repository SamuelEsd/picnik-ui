"""
Isoconversion Handler Component

Manages isoconversion analysis execution and results display.
"""

from typing import Optional, Tuple
import streamlit as st
import pandas as pd

from src.utils.SessionManager import SessionManager
from src.config import DEFAULT_ISO_DA


class IsoconversionHandler:
    """Component for handling isoconversion analysis."""

    def handle_isoconversion(self) -> None:
        """Execute isoconversion analysis and display results."""
        if not SessionManager.get("run_isoconversion_clicked"):
            return

        data_extractor = SessionManager.get("data_extractor")

        if data_extractor is None:
            st.error("No extracted data available for isoconversion.")
            return

        try:
            # Get d_a parameter from session or use default
            d_a = SessionManager.get("isoconversion_d_a", DEFAULT_ISO_DA)

            with st.spinner("Running isoconversion analysis..."):
                temp_df, time_df, diff_df = self._run_isoconversion(data_extractor, d_a)

            if temp_df is None:
                st.error("Isoconversion calculation failed.")
                return

            st.success("Isoconversion analysis completed")

            # Display results
            self._display_isoconversion_results(temp_df, time_df, diff_df)

            # Clear the button state
            SessionManager.set("run_isoconversion_clicked", False)

        except Exception as e:
            st.error(f"Error during isoconversion analysis: {str(e)}")

    def render_isoconversion_controls(self) -> None:
        """Display isoconversion parameter controls."""
        st.divider()
        st.subheader("Isoconversion Analysis")

        col1, col2 = st.columns([3, 1])

        with col1:
            d_a = st.slider(
                "Conversion step size (d_a)",
                min_value=0.001,
                max_value=0.1,
                value=SessionManager.get("isoconversion_d_a", DEFAULT_ISO_DA),
                step=0.001,
                help="Step size between conversion values for isoconversion calculations",
                key="isoconv_d_a_slider",
            )
            SessionManager.set("isoconversion_d_a", d_a)

        with col2:
            st.write("")
            st.write("")
            if st.button("Run Isoconversion", type="primary", key="isoconv_run_btn"):
                SessionManager.set("run_isoconversion_clicked", True)

    def _run_isoconversion(
        self, data_extractor, d_a: float
    ) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Execute isoconversion calculation.

        Args:
            data_extractor: DataExtraction instance.
            d_a (float): Conversion step size.

        Returns:
            Tuple of (TempAdvIsoDF, timeAdvIsoDF, diffAdvIsoDF) or (None, None, None) on error.
        """
        try:
            temp_df, time_df, diff_df = data_extractor.Isoconversion(d_a=d_a)
            return temp_df, time_df, diff_df
        except Exception as e:
            st.error(f"Isoconversion failed: {str(e)}")
            return None, None, None

    def _display_isoconversion_results(
        self, temp_df: pd.DataFrame, time_df: pd.DataFrame, diff_df: pd.DataFrame
    ) -> None:
        """
        Display isoconversion results with download options.

        Args:
            temp_df: Temperature isoconversion DataFrame.
            time_df: Time isoconversion DataFrame.
            diff_df: Conversion rate isoconversion DataFrame.
        """
        st.subheader("Isoconversion Results")

        # Create tabs for different data types
        tab1, tab2, tab3 = st.tabs(
            ["Temperature (K)", "Time (min)", "Conversion Rate (da/dt)"]
        )

        with tab1:
            st.dataframe(temp_df, width='stretch')
            csv_temp = self._dataframe_to_csv(temp_df, "Isoconversion_Temperature")
            st.download_button(
                label="Download Temperature Data (CSV)",
                data=csv_temp,
                file_name="isoconversion_temperature.csv",
                mime="text/csv",
                key="download_temp_iso",
            )

        with tab2:
            st.dataframe(time_df, width='stretch')
            csv_time = self._dataframe_to_csv(time_df, "Isoconversion_Time")
            st.download_button(
                label="Download Time Data (CSV)",
                data=csv_time,
                file_name="isoconversion_time.csv",
                mime="text/csv",
                key="download_time_iso",
            )

        with tab3:
            st.dataframe(diff_df, width='stretch')
            csv_diff = self._dataframe_to_csv(diff_df, "Isoconversion_Rate")
            st.download_button(
                label="Download Conversion Rate Data (CSV)",
                data=csv_diff,
                file_name="isoconversion_rate.csv",
                mime="text/csv",
                key="download_diff_iso",
            )

        # Store results in session for later use
        SessionManager.set("isoconversion_results", [temp_df, time_df, diff_df])
        SessionManager.set("isoconversion_results_dict", {
            "temperature": temp_df,
            "time": time_df,
            "conversion_rate": diff_df
        })

    def _dataframe_to_csv(self, df: pd.DataFrame, label: str = "") -> str:
        """
        Convert DataFrame to CSV string.

        Args:
            df: DataFrame to convert.
            label: Optional label for the CSV.

        Returns:
            CSV string.
        """
        csv_string = df.to_csv(index=True)
        return csv_string
