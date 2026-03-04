"""
Plot management and visualization utilities.
"""

import streamlit as st
from typing import Optional, List, Tuple
from src.ui.PlotlyPlotter import PlotlyPlotter as PP
from src.config import (
    PLOT_X_DATA_OPTIONS, PLOT_Y_DATA_OPTIONS,
    PLOT_X_UNITS, PLOT_Y_UNITS
)
import streamlit.components.v1 as components


class PlotManager:
    """Manages plot creation, display, and range adjustments."""

    def __init__(self, data_extractor=None):
        """
        Initialize PlotManager.
        
        Args:
            data_extractor: DataExtraction instance for generating plots.
        """
        self.data_extractor = data_extractor
        self.plotly_plotters = {}
        self.last_plotly_plotter = None
        self.x_ranges = []

    def get_x_ranges(self) -> Tuple[float, float]:
        return self.x_ranges

    def generate_plot_tabs(self) -> List[str]:
        """
        Generate list of all available plot combinations.
        
        Returns:
            List[str]: List of plot tab labels.
        """
        tabs = []
        for x_data in PLOT_X_DATA_OPTIONS:
            for y_data in PLOT_Y_DATA_OPTIONS:
                for x_unit in PLOT_X_UNITS.get(x_data, []):
                    for y_unit in PLOT_Y_UNITS.get(y_data, []):
                        tabs.append(f"{x_data} ({x_unit}) vs {y_data} ({y_unit})")
        return tabs

    def parse_tab_name(self, tab_name: str) -> Tuple[str, str, str, str]:
        """
        Parse a tab name into its components.
        
        Args:
            tab_name (str): The tab name string.
            
        Returns:
            Tuple of (x_data, x_unit, y_data, y_unit).
        """
        parts = tab_name.split(" ")
        x_data = parts[0]
        x_unit = tab_name.split("(")[1].split(")")[0]
        y_data = tab_name.split("vs")[1].split("(")[0].strip()
        y_unit = tab_name.split("vs")[1].split("(")[1].split(")")[0]
        return x_data, x_unit, y_data, y_unit

    def create_plot(self, x_data: str, y_data: str, x_unit: str, y_unit: str) -> Optional[PP]:
        """
        Create a PlotlyPlotter instance for given data and units.
        
        Args:
            x_data (str): X-axis data type.
            y_data (str): Y-axis data type.
            x_unit (str): X-axis unit.
            y_unit (str): Y-axis unit.
            
        Returns:
            PlotlyPlotter instance or None if data_extractor not available.
        """
        if not self.data_extractor:
            st.error("No data extractor available for plotting.")
            return None

        try:
            matplotlib_figure = self.data_extractor.plot_data(
                x_data=x_data,
                y_data=y_data,
                x_units=x_unit,
                y_units=y_unit
            )
            
            plotly_plotter = PP(
                title=f"{x_data} ({x_unit}) vs {y_data} ({y_unit})",
                x_label=f"{x_data} [{x_unit}]",
                y_label=f"{y_data} [{y_unit}]",
                from_matplotlib_fig=matplotlib_figure
            )
            return plotly_plotter
        except KeyError as e:
            st.error(f"Invalid plot combination: {str(e)}")
            return None

    def display_plot_range_controls(self, plot_idx: int, plotter: PP, placeholder=None) -> None:
        """
        Display interactive range adjustment controls for a plot.
        
        Args:
            plot_idx (int): Index of the plot/tab.
            plotter (PlotlyPlotter): The PlotlyPlotter instance.
            placeholder: Streamlit placeholder container for updates.
        """
        with st.expander("Adjust curve x-ranges (changes applied on button)", expanded=False):
            trace_count = len(getattr(plotter, 'fig').data)
            if trace_count == 0:
                st.write("No traces available for this plot.")
                return

            slider_keys = self._render_range_sliders(plot_idx, plotter, trace_count)
            self._render_range_buttons(plot_idx, plotter, placeholder, slider_keys)

    def _render_range_sliders(self, plot_idx: int, plotter: PP, trace_count: int) -> List[Tuple[int, str]]:
        """
        Render range adjustment sliders for all traces.
        
        Args:
            plot_idx (int): Index of the plot.
            plotter (PlotlyPlotter): The PlotlyPlotter instance.
            trace_count (int): Number of traces.
            
        Returns:
            List of (trace_index, key) tuples.
        """
        slider_keys = []
        for ti in range(trace_count):
            tr = plotter.fig.data[ti]
            name = getattr(tr, 'name', f'trace_{ti}') or f'trace_{ti}'

            # Get bounds for each curve
            self.x_ranges.append(self._get_trace_bounds(plotter, ti))
            bound_min = self.x_ranges[ti][0]
            bound_max = self.x_ranges[ti][1]
            curr_min, curr_max = self._get_current_range(plotter, ti, bound_min, bound_max)

            key = f"tmp_range_{plot_idx}_{ti}"
            slider_keys.append((ti, key))

            # Render slider with color styling
            self._render_styled_slider(name, bound_min, bound_max, curr_min, curr_max, key, plotter, ti)

        return slider_keys

    def _get_trace_bounds(self, plotter: PP, trace_idx: int) -> Tuple[float, float]:
        """Get min/max bounds for a trace."""
        try:
            orig_x = plotter._original_data[trace_idx]['x']
            return float(min(orig_x)), float(max(orig_x))
        except Exception:
            tr = plotter.fig.data[trace_idx]
            xs = list(getattr(tr, 'x', []) or [])
            if xs:
                return float(min(xs)), float(max(xs))
            return 0.0, 1.0

    def _get_current_range(self, plotter: PP, trace_idx: int, default_min: float, default_max: float) -> Tuple[float, float]:
        """Get current x-range for a trace."""
        try:
            curr_min, curr_max = plotter.get_curve_xrange(trace_idx)
            if curr_min is None or curr_max is None:
                return default_min, default_max
            return curr_min, curr_max
        except Exception:
            return default_min, default_max
        
    def _colored_slider(self,label, min_value, max_value, value, key, color, unselected_color="#e0e0e0"):
        st.markdown(f"""
            <style>
                /* Thumb circles */
                [data-baseweb="slider"]:has([aria-label="{label}"])
                [role="slider"] {{
                    background-color: {color} !important;
                    border-color: {color} !important;
                }}
            </style>
        """, unsafe_allow_html=True)
        result = st.slider(label, min_value=min_value, max_value=max_value, value=value, key=key)

        components.html(f"""
            <script>
            function updateSliderColor() {{
                const doc = window.parent.document;
                const sliders = doc.querySelectorAll('[data-baseweb="slider"]');

                for (const slider of sliders) {{
                    // Match slider by aria-label on the thumb
                    const thumb = slider.querySelector('[aria-label="{label}"]');
                    if (!thumb) continue;

                    const track = slider.querySelector('[style*="height: 0.25rem"]');
                    const thumbs = slider.querySelectorAll('[role="slider"]');
                    if (!track || thumbs.length < 2) continue;

                    const min  = parseFloat(thumbs[0].getAttribute('aria-valuemin'));
                    const max  = parseFloat(thumbs[1].getAttribute('aria-valuemax'));
                    const val1 = parseFloat(thumbs[0].getAttribute('aria-valuenow'));
                    const val2 = parseFloat(thumbs[1].getAttribute('aria-valuenow'));

                    const pct1 = ((val1 - min) / (max - min)) * 100;
                    const pct2 = ((val2 - min) / (max - min)) * 100;

                    track.style.setProperty(
                        'background',
                        `linear-gradient(to right,
                            {unselected_color} ${{pct1}}%,
                            {color} ${{pct1}}%,
                            {color} ${{pct2}}%,
                            {unselected_color} ${{pct2}}%
                        )`,
                        'important'
                    );
                }}
            }}

            // Run once on load, then watch for thumb movement
            updateSliderColor();

            const observer = new MutationObserver(updateSliderColor);
            observer.observe(window.parent.document.body, {{
                subtree: true,
                attributes: true,
                attributeFilter: ['aria-valuenow']
            }});
            </script>
        """, height=0)

        return result
    def _render_styled_slider(self, name: str, bound_min: float, bound_max: float,
                            curr_min: float, curr_max: float, key: str, plotter: PP, trace_idx: int) -> None:
        """Render a slider with color styling and synchronized number inputs for a trace."""
        try:
            curve_color = plotter.get_curve_color_rgb_string(trace_idx)
        except Exception as e:
            curve_color = None
            st.warning(f"Color error for {name}: {str(e)}")

        # Initialize session state keys for min/max inputs BEFORE any widget rendering
        key_min_input = f"{key}_min_input"
        key_max_input = f"{key}_max_input"
        
        if key_min_input not in st.session_state:
            st.session_state[key_min_input] = float(curr_min)
        if key_max_input not in st.session_state:
            st.session_state[key_max_input] = float(curr_max)
        if key not in st.session_state:
            st.session_state[key] = (float(curr_min), float(curr_max))


        # Main layout: slider | inputs+color
        col1, col2 = st.columns([3, 1])
        
        with col1:
            slider_value = self._colored_slider(
                label=f"{name} — x range",
                min_value=bound_min,
                max_value=bound_max,
                value=(st.session_state[key_min_input], st.session_state[key_max_input]),
                key=key + "_slider",
                color=curve_color or "#1f77b4"
            )
            # Update session state AFTER slider is created
            st.session_state[key_min_input] = slider_value[0]
            st.session_state[key_max_input] = slider_value[1]
        
        with col2:
            # Subcolumns for min/max inputs
            input_col1, input_col2 = st.columns(2)
            
            with input_col1:
                min_input = st.number_input(
                    "Min",
                    min_value=bound_min,
                    max_value=bound_max,
                    value=st.session_state[key_min_input],
                    key=key_min_input,
                    label_visibility="collapsed"
                )
                # Validate and sync min input with slider
                """
                 min_input = max(bound_min, min(min_input, bound_max))
                if min_input > st.session_state[key_max_input]:
                    min_input = st.session_state[key_max_input]
                st.session_state[key_min_input] = min_input """
            
            with input_col2:
                max_input = st.number_input(
                    "Max",
                    min_value=bound_min,
                    max_value=bound_max,
                    value=st.session_state[key_max_input],
                    key=key_max_input,
                    label_visibility="collapsed"
                )
                """             
                # Validate and sync max input with slider
                max_input = max(bound_min, min(max_input, bound_max))
                if max_input < st.session_state[key_min_input]:
                    max_input = st.session_state[key_min_input]
                st.session_state[key_max_input] = max_input
                """


    def _render_range_buttons(self, plot_idx: int, plotter: PP, placeholder, slider_keys: List[Tuple[int, str]]) -> None:
        """Render Apply and Reset buttons for range adjustments."""
        col_apply, col_reset = st.columns([1, 1])
        with col_apply:
            if st.button("Apply changes", key=f"apply_ranges_{plot_idx}"):
                applied = 0
                for ti, key in slider_keys:
                    vals = st.session_state.get(key)
                    if vals is None:
                        continue
                    try:
                        mn, mx = float(vals[0]), float(vals[1])
                        plotter.update_curve_xrange(ti, x_min=mn, x_max=mx)
                        applied += 1
                    except Exception:
                        continue
                if applied:
                    try:
                        plotter.show(container=placeholder) if placeholder is not None else plotter.show()
                    except Exception:
                        pass
                    st.success(f"Applied ranges to {applied} trace(s) on this plot")
        with col_reset:
            if st.button("Reset sliders", key=f"reset_ranges_{plot_idx}"):
                for ti, key in slider_keys:
                    try:
                        curr = plotter.get_curve_xrange(ti)
                        if curr and curr[0] is not None:
                            st.session_state[key] = (float(curr[0]), float(curr[1]))
                    except Exception:
                        pass
