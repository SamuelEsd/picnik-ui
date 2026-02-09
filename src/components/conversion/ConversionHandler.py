"""
Conversion Handler Component

Manages conversion and isoconversion analysis execution.
"""

from typing import List, Tuple, Optional

import streamlit as st

from src.core.ConversionManager import ConversionManager
from src.utils.SessionManager import SessionManager
from src.ui.PlotlyPlotter import PlotlyPlotter as PP


class ConversionHandler:
    """Component for handling conversion analysis."""

    def handle_conversion(self) -> None:
        """Execute conversion and isoconversion analysis."""
        if not SessionManager.get("run_conversion_clicked"):
            return

        data_extractor = SessionManager.get("data_extractor")
        Bnum = SessionManager.get("Bnum")

        if data_extractor is None or Bnum is None:
            st.error("No extracted data available for conversion.")
            return

        try:
            st.info("Running conversion analysis...")

            conversion_manager = ConversionManager(data_extractor)

            # Get temperature ranges
            ranges = SessionManager.get("conversion_ranges")
            Ti_list, Tf_list = self._prepare_temperature_ranges(
                ranges, Bnum, data_extractor
            )

            # Execute conversion
            conversion_figure = conversion_manager.run_conversion(
                Ti_list, Tf_list
            )

            if conversion_figure is None:
                st.error("Conversion calculation failed.")
                return

            st.success("Conversion analysis completed")

            # Display results
            self._display_results(conversion_figure, Ti_list, Tf_list, Bnum)


        except Exception as e:
            st.error(f"Error during conversion analysis: {str(e)}")

    def _prepare_temperature_ranges(
        self, ranges: Optional[dict], Bnum: list, data_extractor
    ) -> Tuple[List[float], List[float]]:
        """
        Prepare temperature ranges for conversion.

        Args:
            ranges: Conversion ranges from session.
            Bnum: List of B numbers.
            data_extractor: DataExtraction instance.

        Returns:
            Tuple of (Ti_list, Tf_list).
        """
        # Use configured ranges if available and valid, otherwise use defaults
        if ranges and len(ranges) == len(Bnum):
            try:
                Ti_list = [r[0] for r in ranges.values() if r[0] is not None]
                Tf_list = [r[1] for r in ranges.values() if r[1] is not None]
                # Only use configured ranges if all values are valid
                if len(Ti_list) == len(Bnum) and len(Tf_list) == len(Bnum):
                    return Ti_list, Tf_list
            except (TypeError, ValueError):
                pass
        
        # Use default: first to last temperature for each dataset
        Ti_list = [
            data_extractor.DFlis[k]["Temperature [K]"].values[0]
            for k in range(len(Bnum))
        ]
        Tf_list = [
            data_extractor.DFlis[k]["Temperature [K]"].values[-1]
            for k in range(len(Bnum))
        ]
        return Ti_list, Tf_list

    def _display_results(
        self,
        conversion_figure,
        Ti_list: List[float],
        Tf_list: List[float],
        Bnum: list,
    ) -> None:
        """
        Display conversion results and save to session.

        Args:
            conversion_figure: Matplotlib figure from conversion.
            Ti_list: Initial temperatures.
            Tf_list: Final temperatures.
            Bnum: List of B numbers.
        """
        col1, col2 = st.columns([2, 1])

        with col1:
            plotly_plotter = PP(
                title="Conversion",
                x_label="Temperature [K]",
                y_label="TG [%]",
                from_matplotlib_fig=conversion_figure,
            )

            # Apply saved ranges from session if available
            saved_ranges = SessionManager.get("conversion_ranges", {})
            if saved_ranges:
                for trace_idx, (x_min, x_max) in saved_ranges.items():
                    if x_min is not None or x_max is not None:
                        try:
                            plotly_plotter.update_curve_xrange(trace_idx, x_min, x_max)
                        except (IndexError, ValueError):
                            # Skip if trace index doesn't exist for this plot
                            pass
            placeholder = st.empty()
            plotly_plotter.show(container=placeholder)
            
            # Save plotter to session
            SessionManager.set("conversion_plotter", plotly_plotter)

        with col2:
            st.subheader("Analysis Summary")
            st.write(f"Datasets analyzed: **{len(Bnum)}**")
            st.write("Temperature ranges:")
            for i, (ti, tf) in enumerate(zip(Ti_list, Tf_list)):
                st.write(f"  • Dataset {i + 1}: {ti:.1f} K → {tf:.1f} K")
        
        # Save conversion metadata to session
        SessionManager.set("conversion_metadata", {
            "Ti_list": Ti_list,
            "Tf_list": Tf_list,
            "Bnum": Bnum,
        })
