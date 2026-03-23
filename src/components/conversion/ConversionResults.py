"""
Conversion Results Display Component

Displays conversion analysis results and data.
"""

import streamlit as st

from src.utils.SessionManager import SessionManager
from src.config import SESS_BNUM, SESS_CONVERSION_RANGES


class ConversionResults:
    """Component for displaying conversion results."""

    def render(self) -> None:
        """Display conversion analysis results."""
        Bnum = SessionManager.get(SESS_BNUM)
        if Bnum is None:
            st.info("No conversion data available.")
            return

        st.header("Conversion Results")

        # Placeholder for results display
        st.info("Results display will be implemented here")

    def render_summary(self) -> None:
        """Display a summary of conversion analysis."""
        ranges = SessionManager.get(SESS_CONVERSION_RANGES)
        Bnum = SessionManager.get(SESS_BNUM)

        if ranges and Bnum:
            st.write("**Conversion Analysis Summary:**")
            for idx, (min_temp, max_temp) in enumerate(ranges.values()):
                st.write(f"  • Dataset {idx + 1}: {min_temp:.2f} K → {max_temp:.2f} K")
        else:
            st.info("No conversion analysis completed yet.")
