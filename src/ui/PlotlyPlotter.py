
# New class for Plotly plotting
import plotly.graph_objects as go
import streamlit as st
import seaborn as sns
import matplotlib.colors as mcolors


class PlotlyPlotter:
    """
    A class for creating and displaying interactive Plotly plots with multiple curves.
    Can also convert a matplotlib figure to a Plotly figure.
    """
    def __init__(self, title="Plotly Plot", x_label="X", y_label="Y", from_matplotlib_fig=None):
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        if from_matplotlib_fig is not None:
            # Extract colors from matplotlib figure before conversion
            extracted_colors = self._extract_colors_from_matplotlib(from_matplotlib_fig)
            self.fig = self._from_matplotlib(from_matplotlib_fig)
            
            # Create palette from extracted colors, or fallback to husl
            if extracted_colors:
                self.color_palette = sns.color_palette(extracted_colors)
            else:
                num_curves = len(self.fig.data)
                self.color_palette = sns.color_palette("husl", n_colors=num_curves) if num_curves > 0 else []
        else:
            self.fig = go.Figure()
            self.color_palette = []
        self._original_data = []
        self._current_ranges = {}
        
        # Initialize _original_data and _current_ranges for existing traces (e.g., from matplotlib conversion)
        for idx, trace in enumerate(self.fig.data):
            x_data = list(trace.x) if getattr(trace, 'x', None) is not None else []
            y_data = list(trace.y) if getattr(trace, 'y', None) is not None else []
            self._original_data.append({
                "x": x_data,
                "y": y_data,
                "name": getattr(trace, 'name', None),
                "mode": getattr(trace, 'mode', 'lines+markers'),
                "line": getattr(trace, 'line', None),
                "marker": getattr(trace, 'marker', None),
            })
            self._current_ranges[idx] = (None, None)
            

    def _extract_colors_from_matplotlib(self, mpl_fig):
        """
        Extract the colors of all curves in a matplotlib figure.
        Returns a list of RGB color tuples (values in range [0, 1]).
        """
        colors = []
        try:
            for ax in mpl_fig.axes:
                for line in ax.get_lines():
                    color = line.get_color()
                    # Convert color name or hex to RGBA
                    if isinstance(color, str):
                        try:
                            rgba = mcolors.to_rgba(color)
                            colors.append(rgba[:3])  # Return just RGB, ignore alpha
                        except (ValueError, AttributeError) as e:
                            print(f"Warning: Could not convert color '{color}' to RGBA: {e}")
                    else:
                        # Already a tuple/array
                        colors.append(color[:3] if len(color) >= 3 else color)
        except Exception as e:
            print(f"Warning: Failed to extract colors from matplotlib figure: {e}")
        
        return colors

    def _rgb_to_string(self, rgb_color):
        """
        Convert RGB color tuple (values in range [0, 1]) to RGB string format.
        
        Args:
            rgb_color (tuple): RGB color tuple (r, g, b) with values in range [0, 1].
            
        Returns:
            str: Color in 'rgb(r, g, b)' format.
        """
        return f"rgb({int(rgb_color[0]*255)}, {int(rgb_color[1]*255)}, {int(rgb_color[2]*255)})"

    def _resolve_trace_indices(self, identifier):
        """
        Resolve an identifier (int index or str name) to a list of trace indices.
        
        Args:
            identifier (int|str): Trace index (0-based) or trace name.
            
        Returns:
            list: List of trace indices matching the identifier.
            
        Raises:
            IndexError: If int identifier is out of range.
            ValueError: If str identifier not found.
            TypeError: If identifier is neither int nor str.
        """
        if isinstance(identifier, int):
            if identifier < 0 or identifier >= len(self.fig.data):
                raise IndexError("Trace index out of range")
            return [identifier]
        elif isinstance(identifier, str):
            indices = [i for i, tr in enumerate(self.fig.data) if (getattr(tr, "name", None) == identifier)]
            if not indices:
                raise ValueError(f"No trace found with name '{identifier}'")
            return indices
        else:
            raise TypeError("Identifier must be an int (index) or str (name)")

    def _filter_xy_by_range(self, x_vals, y_vals, x_min=None, x_max=None):
        """
        Filter x and y values based on x range bounds.
        
        Args:
            x_vals (list): X values.
            y_vals (list): Y values.
            x_min (float|None): Minimum x value to keep.
            x_max (float|None): Maximum x value to keep.
            
        Returns:
            tuple: (filtered_x, filtered_y) or (x_vals, y_vals) if no filtering needed.
        """
        if x_min is None and x_max is None:
            return x_vals, y_vals
        
        filtered_x = []
        filtered_y = []
        for xi, yi in zip(x_vals, y_vals):
            if (x_min is None or xi >= x_min) and (x_max is None or xi <= x_max):
                filtered_x.append(xi)
                filtered_y.append(yi)
        return filtered_x, filtered_y

    def add_curve(self, x, y, name=None, mode="lines+markers", line=None, marker=None, x_min=None, x_max=None):
        """
        Add a curve to the plot.
        Args:
            x (array-like): X data
            y (array-like): Y data
            name (str): Name for the legend
            mode (str): Plotly mode (e.g., 'lines', 'markers', 'lines+markers')
            line (dict): Line style dict (optional)
            marker (dict): Marker style dict (optional)
            x_min (float): Minimum x value to include (optional)
            x_max (float): Maximum x value to include (optional)
        """
        # Keep originals (convert to lists in case user passes numpy arrays/iterables)
        orig_x = list(x)
        orig_y = list(y)
        self._original_data.append({
            "x": orig_x,
            "y": orig_y,
            "name": name,
            "mode": mode,
            "line": line,
            "marker": marker,
        })
        # Default: no user-applied bounds
        self._current_ranges[len(self._original_data) - 1] = (None, None)

        # Filter x and y based on x_min and x_max if provided
        x, y = self._filter_xy_by_range(orig_x, orig_y, x_min, x_max)

        self.fig.add_trace(go.Scatter(x=x, y=y, mode=mode, name=name, line=line, marker=marker))

    def get_curve_color(self, curve_index):
        """
        Get the color for a specific curve by its index.
        
        Args:
            curve_index (int): The index of the curve (0-based).
            
        Returns:
            tuple: RGB color tuple (r, g, b) with values in range [0, 1].
            
        Raises:
            IndexError: If curve_index is out of range.
        """
        if curve_index < 0 or curve_index >= len(self.color_palette):
            raise IndexError(f"Curve index {curve_index} out of range. Total curves: {len(self.color_palette)}")
        return self.color_palette[curve_index]

    def get_curve_color_rgb_string(self, curve_index):
        """
        Get the color for a specific curve as an RGB string.
        
        Args:
            curve_index (int): The index of the curve (0-based).
            
        Returns:
            str: Color in 'rgb(r, g, b)' format.
            
        Raises:
            IndexError: If curve_index is out of range.
        """
        rgb_color = self.get_curve_color(curve_index)
        rgb_string = self._rgb_to_string(rgb_color)
        return rgb_string

    def update_curve_xrange(self, identifier, x_min=None, x_max=None):
        """
        Update (trim) the x-range for a specific curve, identified by its
        integer trace index or by its legend name (string). The method uses
        the original x/y data stored when the curve was added and stores the range.

        Args:
            identifier (int|str): Trace index (0-based) or trace name.
            x_min (float|None): Minimum x value to keep.
            x_max (float|None): Maximum x value to keep.
        """
        if not self._original_data:
            raise ValueError("No original curve data available to update ranges.")

        # Resolve indices for the identifier
        indices = self._resolve_trace_indices(identifier)

        # Store the requested current range for the trace(s). This does NOT
        # mutate or trim the original x/y arrays — it only records the desired
        # x_min/x_max for later application.
        for idx in indices:
            try:
                _ = self._original_data[idx]
            except IndexError:
                raise IndexError("Original data for the specified trace is not available")
            self._current_ranges[idx] = (x_min, x_max)

    def get_current_ranges(self):
        """
        Get the current x-ranges for all curves.

        Returns:
            dict: Mapping of trace indices to (x_min, x_max) tuples.
        """
        return self._current_ranges.copy()

    def get_curve_xrange(self, identifier):
        """
        Get the current x-range for a specific curve (trace).

        Args:
            identifier (int|str): Trace index (0-based) or trace name.

        Returns:
            If `identifier` is an int: a tuple `(x_min, x_max)` or `(None, None)` if no data.
            If `identifier` is a str (name): a dict mapping trace indices to `(x_min, x_max)`.
        """
        if not self.fig.data:
            raise ValueError("No traces available in the figure")

        # Resolve indices for the identifier
        indices = self._resolve_trace_indices(identifier)

        results = {}
        for idx in indices:
            # Prefer stored current ranges if available
            if idx < len(self._current_ranges):
                stored = self._current_ranges[idx]
                if stored and (stored[0] is not None or stored[1] is not None):
                    results[idx] = stored
                    continue

            # Fallback: infer from current trace x values
            xs = list(self.fig.data[idx].x) if getattr(self.fig.data[idx], 'x', None) is not None else []
            if not xs:
                results[idx] = (None, None)
            else:
                try:
                    xmin = min(xs)
                    xmax = max(xs)
                except TypeError:
                    try:
                        nums = [float(v) for v in xs]
                        xmin = min(nums)
                        xmax = max(nums)
                    except Exception:
                        results[idx] = (None, None)
                        continue
                results[idx] = (xmin, xmax)

        if isinstance(identifier, int):
            return results[indices[0]]
        return results


    def show(self, use_streamlit=True, container=None):
        """
        Display the plot using Streamlit or in a browser.
        
        Rebuilds the figure from _original_data, applying any stored ranges from
        update_curve_xrange(). This ensures display always reflects the current state.
        
        Args:
            use_streamlit (bool): If True, use st.plotly_chart; else, fig.show().
            container: Optional Streamlit container to render into.
        """
        if self._original_data:
            display_fig = go.Figure()
            for idx, orig in enumerate(self._original_data):
                x_vals = list(orig.get("x", []))
                y_vals = list(orig.get("y", []))

                # Determine stored range for this trace
                x_min, x_max = (None, None)
                if idx < len(self._current_ranges):
                    x_min, x_max = self._current_ranges[idx]

                # Filter by range if specified
                disp_x, disp_y = self._filter_xy_by_range(x_vals, y_vals, x_min, x_max)

                display_fig.add_trace(
                    go.Scatter(
                        x=disp_x,
                        y=disp_y,
                        mode=orig.get("mode"),
                        name=orig.get("name"),
                        line=orig.get("line"),
                        marker=orig.get("marker"),
                    )
                )

            display_fig.update_layout(title=self.title, xaxis_title=self.x_label, yaxis_title=self.y_label)
            if use_streamlit:
                if container is not None:
                    try:
                        container.plotly_chart(display_fig, width='stretch')
                        return
                    except Exception:
                        # Fallback to global st if container fails
                        pass
                st.plotly_chart(display_fig, width='stretch')
            else:
                display_fig.show()
        else:
            # Fallback: if no original_data recorded, just display the internal figure as-is.
            self.fig.update_layout(title=self.title, xaxis_title=self.x_label, yaxis_title=self.y_label)
            if use_streamlit:
                if container is not None:
                    try:
                        container.plotly_chart(self.fig, width='stretch')
                        return
                    except Exception:
                        pass
                st.plotly_chart(self.fig, width='stretch')
            else:
                self.fig.show()

    def _from_matplotlib(self, mpl_fig):
        try:
            import warnings
            import plotly.tools as tls
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="I found a path object")
                plotly_fig = tls.mpl_to_plotly(mpl_fig)
            return plotly_fig
        except ImportError:
            raise ImportError("plotly.tools.mpl_to_plotly is required for matplotlib conversion. Please install plotly >=4.0.")
        except Exception as e:
            raise RuntimeError(f"Failed to convert matplotlib figure: {e}")
