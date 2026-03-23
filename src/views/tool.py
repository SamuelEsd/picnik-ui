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
from src.components.conversion import (
    ConversionControls,
    ConversionHandler,
    IsoconversionHandler,
)
from src.components.kinetics import (
    ActivationEnergyHandler,
    CompensationEffectHandler,
    ReconstructionHandler,
    PredictionHandler,
)


def main():
    """Main application flow using modular components."""
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

    # ------------------------------------------------------------------ #
    # STEP 1-2: Data Input                                                 #
    # ------------------------------------------------------------------ #

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

    # ------------------------------------------------------------------ #
    # STEP 2: Data Extraction                                              #
    # ------------------------------------------------------------------ #

    # Component 5: Extraction Controls and Handler
    extraction_controls = ExtractionControls()
    extraction_controls.render()

    extraction_handler = ExtractionHandler()
    if not extraction_handler.handle_extraction():
        return

    # Component 6: Plot Viewer
    plot_viewer = PlotViewer()
    plot_viewer.render()

    # ------------------------------------------------------------------ #
    # STEP 3-4: Conversion & Isoconversion                                 #
    # ------------------------------------------------------------------ #

    # Component 7: Conversion Controls and Handler
    conversion_controls = ConversionControls()
    conversion_controls.render()

    conversion_handler = ConversionHandler()
    conversion_handler.handle_conversion()

    # Component 8: Isoconversion Controls and Handler
    isoconversion_handler = IsoconversionHandler()
    isoconversion_handler.render_isoconversion_controls()
    isoconversion_handler.handle_isoconversion()

    # ------------------------------------------------------------------ #
    # STEP 5: Activation Energy                                            #
    # ------------------------------------------------------------------ #

    activation_energy_handler = ActivationEnergyHandler()
    if activation_energy_handler.setup():
        activation_energy_handler.render_activation_energy_controls()
        activation_energy_handler.handle_activation_energy()

    # ------------------------------------------------------------------ #
    # STEP 6: Compensation Effect (Pre-exponential Factor)                 #
    # ------------------------------------------------------------------ #

    comp_handler = CompensationEffectHandler()
    comp_handler.render_compensation_controls()
    comp_handler.handle_compensation_effect()

    # ------------------------------------------------------------------ #
    # STEP 7: Reaction Model Reconstruction — g(alpha)                    #
    # ------------------------------------------------------------------ #

    recon_handler = ReconstructionHandler()
    recon_handler.render_reconstruction_controls()
    recon_handler.handle_reconstruction()

    # ------------------------------------------------------------------ #
    # STEP 8: Kinetic Predictions                                          #
    # ------------------------------------------------------------------ #

    pred_handler = PredictionHandler()
    pred_handler.render_prediction_controls()
    pred_handler.handle_predictions()


if __name__ == "__main__":
    main()
