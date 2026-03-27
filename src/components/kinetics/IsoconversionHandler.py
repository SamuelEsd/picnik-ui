"""
Isoconversion Handler Component

Manages isoconversion analysis execution and results display.
"""

import streamlit as st
import pandas as pd

from src.utils.SessionManager import SessionManager
from src.config import (
    DEFAULT_ISO_DA, SESS_DATA_EXTRACTOR, SESS_ISOCONVERSION_RESULT,
    SESS_RUN_ISOCONVERSION, SESS_ISO_DA, SESS_ACTIVATION_ENERGY_OBJECT,
    SESS_ACTIVATION_ENERGY_RESULTS, SESS_COMP_RESULTS, SESS_RECON_RESULTS,
)
from src.models.results import IsoconversionResults


class IsoconversionHandler:
    """Component for handling isoconversion analysis."""

    def handle_isoconversion(self) -> None:
        """Execute isoconversion analysis and display results."""
        if SessionManager.get(SESS_RUN_ISOCONVERSION):
            data_extractor = SessionManager.get(SESS_DATA_EXTRACTOR)

            if data_extractor is None:
                st.error("No extracted data available for isoconversion.")
            else:
                try:
                    d_a = SessionManager.get(SESS_ISO_DA, DEFAULT_ISO_DA)

                    with st.spinner("Running isoconversion analysis..."):
                        temp_df, time_df, diff_df = data_extractor.Isoconversion(d_a=d_a)

                    st.success("Isoconversion analysis completed")
                    SessionManager.set(
                        SESS_ISOCONVERSION_RESULT,
                        IsoconversionResults(
                            temperature=temp_df,
                            time=time_df,
                            conversion_rate=diff_df,
                        ),
                    )
                    # Isoconversion inputs changed — invalidate all downstream objects
                    # so they are rebuilt with the new tables on the next run.
                    SessionManager.delete(SESS_ACTIVATION_ENERGY_OBJECT)
                    SessionManager.delete(SESS_ACTIVATION_ENERGY_RESULTS)
                    SessionManager.delete(SESS_COMP_RESULTS)
                    SessionManager.delete(SESS_RECON_RESULTS)

                except Exception as e:
                    st.error(f"Error during isoconversion analysis: {str(e)}")

            SessionManager.set(SESS_RUN_ISOCONVERSION, False)

        # Always display from session if results exist
        iso_results = SessionManager.get(SESS_ISOCONVERSION_RESULT)
        if iso_results is not None:
            self._display_isoconversion_results(iso_results)

    def _display_isoconversion_results(self, results: IsoconversionResults) -> None:
        """Display isoconversion results with download options."""
        st.subheader("Isoconversion Results")

        tab1, tab2, tab3 = st.tabs(
            ["Temperature (K)", "Time (min)", "Conversion Rate (∆α/∆t)"]
        )

        with tab1:
            st.dataframe(results.temperature, width='stretch')
            st.download_button(
                label="Download Temperature Data (CSV)",
                data=results.temperature.to_csv(index=True),
                file_name="isoconversion_temperature.csv",
                mime="text/csv",
                key="download_temp_iso",
            )

        with tab2:
            st.dataframe(results.time, width='stretch')
            st.download_button(
                label="Download Time Data (CSV)",
                data=results.time.to_csv(index=True),
                file_name="isoconversion_time.csv",
                mime="text/csv",
                key="download_time_iso",
            )

        with tab3:
            st.dataframe(results.conversion_rate, width='stretch')
            st.download_button(
                label="Download Conversion Rate Data (CSV)",
                data=results.conversion_rate.to_csv(index=True),
                file_name="isoconversion_rate.csv",
                mime="text/csv",
                key="download_diff_iso",
            )
