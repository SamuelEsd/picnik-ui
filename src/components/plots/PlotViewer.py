"""
Plot Viewer Component

Displays interactive plots with tabs.
"""

import streamlit as st

from src.utils.SessionManager import SessionManager
from src.ui.PlotManager import PlotManager
from src.ui.PlotlyPlotter import PlotlyPlotter as PP
from src.config import SESS_DATA_EXTRACTOR, SESS_CONVERSION_RANGES, SESS_PLOTLY_PLOTTERS


class PlotViewer:
    """Component for displaying interactive plots."""

    def render(self) -> None:
        """Display all available plot combinations with interactive controls."""
        data_extractor = SessionManager.get(SESS_DATA_EXTRACTOR)
        if data_extractor is None:
            st.info("Extract data first to display plots.")
            return

        st.divider()
        st.subheader("Step 4: Interactive Plots")

        plot_manager = PlotManager(data_extractor)
        plot_tabs = plot_manager.generate_plot_tabs()

        tabs = st.tabs(plot_tabs)

        for idx, tab in enumerate(tabs):
            with tab:
                self._render_plot_tab(idx, plot_manager, plot_tabs)

    def _render_plot_tab(self, idx: int, plot_manager: PlotManager, plot_tabs: list) -> None:
        """
        Render a single plot tab.

        Args:
            idx: Tab index.
            plot_manager: PlotManager instance.
            plot_tabs: List of plot tab names.
        """
        try:
            x_data, x_unit, y_data, y_unit = plot_manager.parse_tab_name(plot_tabs[idx])

            # Create plot
            plotter = plot_manager.create_plot(x_data, y_data, x_unit, y_unit)

            if plotter is None:
                st.error(f"Failed to create plot for {plot_tabs[idx]}")
                return

            # Apply saved ranges from session if available
            saved_ranges = SessionManager.get(SESS_CONVERSION_RANGES, {})
            if saved_ranges:
                for trace_idx, (x_min, x_max) in saved_ranges.items():
                    if x_min is not None or x_max is not None:
                        try:
                            plotter.update_curve_xrange(trace_idx, x_min, x_max)
                        except (IndexError, ValueError):
                            # Skip if trace index doesn't exist for this plot
                            pass

            # Display plot
            placeholder = st.empty()
            plotter.show(container=placeholder)

            # Store plotter in session for later manipulation
            plotters_dict = SessionManager.get(SESS_PLOTLY_PLOTTERS, {})
            plotters_dict[idx] = {"plotter": plotter, "placeholder": placeholder}
            SessionManager.set(SESS_PLOTLY_PLOTTERS, plotters_dict)

            # Display range controls for interactive adjustment
            if idx == 0:
                plot_manager.display_plot_range_controls(idx, plotter, placeholder)
                plotter_current_ranges = plotter.get_current_ranges()
                SessionManager.set(SESS_CONVERSION_RANGES, plotter_current_ranges)

        except KeyError as e:
            st.error(f"Invalid plot combination: {str(e)}")
        except Exception as e:
            st.error(f"Error creating plot: {str(e)}")
