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
        data_extractor = st.session_state.get(SESS_DATA_EXTRACTOR)
        if data_extractor is None:
            st.info("Extract data first to display plots.")
            return

        st.divider()
        st.subheader("Step 4: Interactive Plots")

        plot_manager = PlotManager(data_extractor)
        plot_tabs = plot_manager.generate_plot_tabs()

        # st.tabs() has no way to read back the user's current selection, so
        # a rerun triggered by an unrelated widget elsewhere on the page
        # (e.g. "Run Conversion") silently resets it to the first tab. A
        # keyed segmented_control persists the selection in session state
        # across reruns like any other widget.
        selected_tab = st.segmented_control(
            "Plot",
            options=plot_tabs,
            default=plot_tabs[0],
            key="plot_viewer_selected_tab",
            label_visibility="collapsed",
        )
        if selected_tab not in plot_tabs:
            selected_tab = plot_tabs[0]

        self._render_plot_tab(plot_tabs.index(selected_tab), plot_manager, plot_tabs)

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

            # Reuse the plotter from session state if this tab was already
            # built. picnik's plotting methods go through matplotlib's
            # global pyplot state (plt.gcf()/plt.show()), which is fragile
            # to rebuild on every rerun of the whole app (e.g. clicking
            # "Run Conversion" triggers a full rerun of this page too) -
            # so compute each tab once and cache it here, the same way
            # every other step's results persist in session state.
            plotters_dict = st.session_state.get(SESS_PLOTLY_PLOTTERS, {})
            cached = plotters_dict.get(idx)
            if cached is not None:
                plotter = cached["plotter"]
            else:
                plotter = plot_manager.create_plot(x_data, y_data, x_unit, y_unit)
                if plotter is None:
                    st.error(f"Failed to create plot for {plot_tabs[idx]}")
                    return
                plotters_dict[idx] = {"plotter": plotter}
                st.session_state[SESS_PLOTLY_PLOTTERS] = plotters_dict

            # Apply saved temperature ranges only to temperature-axis plots.
            # Time-axis plots use a completely different x unit (min), so applying
            # Kelvin ranges would filter out all data points.
            if x_data == 'temperature':
                saved_ranges = st.session_state.get(SESS_CONVERSION_RANGES, {})
                if saved_ranges:
                    for trace_idx, (x_min, x_max) in saved_ranges.items():
                        if x_min is not None or x_max is not None:
                            try:
                                plotter.update_curve_xrange(trace_idx, x_min, x_max)
                            except (IndexError, ValueError):
                                # Skip if trace index doesn't exist for this plot
                                pass

            # For time-axis plots, warn that curves are not directly comparable:
            # experiments at different heating rates cover very different time spans,
            # so faster rates appear compressed on the left of the shared x-axis.
            if x_data == 'time':
                st.info(
                    "Each heating rate covers a different total time "
                    "(e.g. β=2 K/min takes ~10x longer than β=20 K/min). "
                    "On a shared time axis, faster experiments appear compressed "
                    "on the left and their transitions may be hard to see. "
                    "Use the temperature plots for direct comparisons."
                )

            # Display plot
            placeholder = st.empty()
            plotter.show(container=placeholder)

            # Display range controls for interactive adjustment
            if idx == 0:
                plot_manager.display_plot_range_controls(idx, plotter, placeholder)
                plotter_current_ranges = plotter.get_current_ranges()
                st.session_state[SESS_CONVERSION_RANGES] = plotter_current_ranges

        except KeyError as e:
            st.error(f"Invalid plot combination: {str(e)}")
        except Exception as e:
            st.error(f"Error creating plot: {str(e)}")
