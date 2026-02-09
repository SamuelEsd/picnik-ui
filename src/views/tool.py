"""
Main Tool View - Using Component-Based Architecture

This view demonstrates how to compose modular components
following a React-like architecture pattern in Streamlit.
"""

import streamlit as st

from src.config import APP_TITLE
from src.components.data_source import DataSourceSelector
from src.components.file_validation import (
    FileCountValidator,
    FileStructureValidator,
    FilePreview,
)
from src.components.extraction import ExtractionControls, ExtractionHandler
from src.components.plots import PlotViewer
from src.components.conversion import ConversionControls, ConversionHandler


def main():
    """Main application flow using modular components."""
    # Page configuration
    st.set_page_config(layout="wide", initial_sidebar_state="expanded")

    # Page title and description
    st.title(APP_TITLE)
    st.write(
        "Web-based data analysis and visualization platform for thermal analysis."
    )
    st.write(
        "Built with Streamlit, Pandas, Plotly, and SciPy for interactive thermal data processing."
    )
    st.write(
        "Learn more about thermal analysis: [GitHub - Picnik](https://github.com/ErickErock/pICNIK)"
    )

    # Component 1: Data Source Selection
    data_source_selector = DataSourceSelector()
    file_paths = data_source_selector.render()
    if not file_paths:
        return

    # Component 2: File Count Validation
    file_count_validator = FileCountValidator()
    if not file_count_validator.validate(file_paths):
        return

    # Component 3: File Structure Validation
    file_structure_validator = FileStructureValidator()
    valid_files, invalid_files = file_structure_validator.validate(file_paths)
    if not valid_files:
        return

    # Component 4: File Preview
    file_preview = FilePreview()
    file_preview.render(valid_files, file_paths)

    # Component 5: Extraction Controls and Handler
    extraction_controls = ExtractionControls()
    extraction_controls.render()

    extraction_handler = ExtractionHandler()
    if not extraction_handler.handle_extraction():
        return

    # Component 6: Plot Viewer
    plot_viewer = PlotViewer()
    plot_viewer.render()

    # Component 7: Conversion Controls and Handler
    conversion_controls = ConversionControls()
    conversion_controls.render()

    conversion_handler = ConversionHandler()
    conversion_handler.handle_conversion()


if __name__ == "__main__":
    main()


