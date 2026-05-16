"""
Main Tool View - Using Component-Based Architecture
"""

import streamlit as st

from src.config import APP_TITLE
from src.i18n import _
from src.components.data_source import DataSourceSelector
from src.components.file_validation import (
    FileCountValidator,
    FileStructureValidator,
    FilePreview,
)
from src.components.extraction import ExtractionControls, ExtractionHandler
from src.components.plots import PlotViewer
from src.components.conversion import ConversionControls, ConversionHandler
from src.components.kinetics import (
    IsoconversionControls, IsoconversionHandler,
    ActivationEnergyControls, ActivationEnergyHandler,
    CompensationEffectControls, CompensationEffectHandler,
    ReconstructionControls, ReconstructionHandler,
    PredictionControls, PredictionHandler,
)


def main():
    """Main application flow using modular components."""
    st.title(APP_TITLE)
    st.write(_("Web-based data analysis and visualization platform for thermal analysis."))
    st.write(_(
        "Built with Streamlit, Pandas, Plotly, and SciPy for interactive thermal data processing."
    ))
    st.write(_(
        "Learn more about thermal analysis: [GitHub - Picnik](https://github.com/ErickErock/pICNIK)"
    ))

    data_source_selector = DataSourceSelector()
    file_paths = data_source_selector.render()
    if not file_paths:
        return

    file_count_validator = FileCountValidator()
    if not file_count_validator.validate(file_paths):
        return

    file_structure_validator = FileStructureValidator()
    valid_files, invalid_files = file_structure_validator.validate(file_paths)
    if not valid_files:
        return

    file_preview = FilePreview()
    file_preview.render(valid_files, file_paths)

    extraction_controls = ExtractionControls()
    extraction_controls.render()

    extraction_handler = ExtractionHandler()
    extraction_handler.handle_extraction()

    plot_viewer = PlotViewer()
    plot_viewer.render()

    conversion_controls = ConversionControls()
    conversion_controls.render()

    conversion_handler = ConversionHandler()
    conversion_handler.handle_conversion()

    IsoconversionControls().render()
    IsoconversionHandler().handle_isoconversion()

    ActivationEnergyControls().render()
    ae_handler = ActivationEnergyHandler()
    if ae_handler.setup():
        ae_handler.handle_activation_energy()

    CompensationEffectControls().render()
    CompensationEffectHandler().handle_compensation_effect()

    ReconstructionControls().render()
    ReconstructionHandler().handle_reconstruction()

    PredictionControls().render()
    PredictionHandler().handle_predictions()


if __name__ == "__main__":
    main()
