"""
Isoconversion Handler Component

Manages isoconversion analysis execution and results display.
"""

import streamlit as st
import pandas as pd

from src.i18n import _
from src.utils.SessionManager import SessionManager
from src.config import (
    DEFAULT_ISO_DA, SESS_DATA_EXTRACTOR, SESS_ISOCONVERSION_RESULT,
    SESS_RUN_ISOCONVERSION, SESS_ISO_DA,
)
from src.models.results import IsoconversionResults


class IsoconversionHandler:
    """Component for handling isoconversion analysis."""

    def handle_isoconversion(self) -> None:
        """Execute isoconversion analysis when triggered and display stored results.

        Reads SESS_RUN_ISOCONVERSION. When True, calls DataExtraction.Isoconversion()
        with the configured Δα step, stores an IsoconversionResults in session state,
        and invalidates all downstream steps (activation energy through predictions).
        Always renders the stored results table at the end of the call.
        """
        if st.session_state.get(SESS_RUN_ISOCONVERSION):
            data_extractor = st.session_state.get(SESS_DATA_EXTRACTOR)

            if data_extractor is None:
                st.error(_("No extracted data available for isoconversion."))
            else:
                try:
                    d_a = st.session_state.get(SESS_ISO_DA, DEFAULT_ISO_DA)

                    with st.spinner(_("Running isoconversion analysis...")):
                        temp_df, time_df, diff_df = data_extractor.Isoconversion(d_a=d_a)

                    st.success(_("Isoconversion analysis completed"))
                    st.session_state[SESS_ISOCONVERSION_RESULT] = IsoconversionResults(
                            temperature=temp_df,
                            time=time_df,
                            conversion_rate=diff_df,
                        )
                    SessionManager.clear_downstream_from("isoconversion")

                except Exception as e:
                    st.error(_("Error during isoconversion analysis: {error}").format(error=str(e)))

            st.session_state[SESS_RUN_ISOCONVERSION] = False

        # Always display from session if results exist
        iso_results = st.session_state.get(SESS_ISOCONVERSION_RESULT)
        if iso_results is not None:
            self._display_isoconversion_results(iso_results)

    def _display_isoconversion_results(self, results: IsoconversionResults) -> None:
        """Render isoconversion tables with per-column download buttons.

        Args:
            results: Stored isoconversion output containing temperature, time,
                and conversion rate DataFrames indexed by α.
        """
        st.subheader(_("Isoconversion Results"))

        tab1, tab2, tab3 = st.tabs(
            [_("Temperature (K)"), _("Time (min)"), _("Conversion Rate (∆α/∆t)")]
        )

        with tab1:
            st.dataframe(results.temperature, width='stretch')
            st.download_button(
                label=_("Download Temperature Data (CSV)"),
                data=results.temperature.to_csv(index=True),
                file_name="isoconversion_temperature.csv",
                mime="text/csv",
                key="download_temp_iso",
            )

        with tab2:
            st.dataframe(results.time, width='stretch')
            st.download_button(
                label=_("Download Time Data (CSV)"),
                data=results.time.to_csv(index=True),
                file_name="isoconversion_time.csv",
                mime="text/csv",
                key="download_time_iso",
            )

        with tab3:
            st.dataframe(results.conversion_rate, width='stretch')
            st.download_button(
                label=_("Download Conversion Rate Data (CSV)"),
                data=results.conversion_rate.to_csv(index=True),
                file_name="isoconversion_rate.csv",
                mime="text/csv",
                key="download_diff_iso",
            )
