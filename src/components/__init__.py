"""
Streamlit UI Components

Modular, reusable components following a React-like architecture.
Each component is independently testable and composable.

Usage:
    from src.components.data_source import DataSourceSelector
    from src.components.file_validation import FileValidator, FilePreview
    from src.components.extraction import ExtractionControls
    from src.components.plots import PlotViewer
    from src.components.conversion import ConversionControls, ConversionResults
"""

__all__ = [
    "DataSourceSelector",
    "FileValidator",
    "FilePreview",
    "ExtractionControls",
    "PlotViewer",
    "ConversionControls",
    "ConversionResults",
]
