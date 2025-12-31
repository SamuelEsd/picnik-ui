
# New class for Plotly plotting
import plotly.graph_objects as go
import streamlit as st


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
            self.fig = self._from_matplotlib(from_matplotlib_fig)
        else:
            self.fig = go.Figure()

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
        # Filter x and y based on x_min and x_max if provided
        if x_min is not None or x_max is not None:
            filtered_x = []
            filtered_y = []
            for xi, yi in zip(x, y):
                if (x_min is None or xi >= x_min) and (x_max is None or xi <= x_max):
                    filtered_x.append(xi)
                    filtered_y.append(yi)
            x = filtered_x
            y = filtered_y
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
