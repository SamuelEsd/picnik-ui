
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
        self._current_ranges = []
            

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
        self._current_ranges.append((None, None))

        # Filter x and y based on x_min and x_max if provided (use originals)
        if x_min is not None or x_max is not None:
            filtered_x = []
            filtered_y = []
            for xi, yi in zip(orig_x, orig_y):
                if (x_min is None or xi >= x_min) and (x_max is None or xi <= x_max):
                    filtered_x.append(xi)
                    filtered_y.append(yi)
            x = filtered_x
            y = filtered_y
        else:
            x = orig_x
            y = orig_y

        self.fig.add_trace(go.Scatter(x=x, y=y, mode=mode, name=name, line=line, marker=marker))


    def show(self, use_streamlit=True):
        """
        Display the plot using Streamlit or in a browser.
        Args:
            use_streamlit (bool): If True, use st.plotly_chart; else, fig.show().
        """
        self.fig.update_layout(title=self.title, xaxis_title=self.x_label, yaxis_title=self.y_label)
        if use_streamlit:
            st.plotly_chart(self.fig, use_container_width=True)
        else:
            self.fig.show()

    def _from_matplotlib(self, mpl_fig):
        try:
            import plotly.tools as tls
            plotly_fig = tls.mpl_to_plotly(mpl_fig)
            return plotly_fig
        except ImportError:
            raise ImportError("plotly.tools.mpl_to_plotly is required for matplotlib conversion. Please install plotly >=4.0.")
        except Exception as e:
            raise RuntimeError(f"Failed to convert matplotlib figure: {e}")
