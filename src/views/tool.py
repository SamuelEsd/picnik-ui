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
from src.components.kinetics import (
    IsoconversionControls, IsoconversionHandler,
    ActivationEnergyControls, ActivationEnergyHandler,
    CompensationEffectControls, CompensationEffectHandler,
    ReconstructionControls, ReconstructionHandler,
    PredictionControls, PredictionHandler,
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
    # STEP 1: Data Source Selection  /  STEP 2: File Validation & Preview  #
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
    # STEP 3: Data Extraction  /  STEP 4: Interactive Plots               #
    # ------------------------------------------------------------------ #

    # Component 5: Extraction Controls and Handler
    extraction_controls = ExtractionControls()
    extraction_controls.render()

    extraction_handler = ExtractionHandler()
    extraction_handler.handle_extraction()

    # Component 6: Plot Viewer
    plot_viewer = PlotViewer()
    plot_viewer.render()

    # ------------------------------------------------------------------ #
    # STEP 5: Conversion  /  STEP 6: Isoconversion                        #
    # ------------------------------------------------------------------ #

    # Component 7: Conversion Controls and Handler
    conversion_controls = ConversionControls()
    conversion_controls.render()

    conversion_handler = ConversionHandler()
    conversion_handler.handle_conversion()

    # Component 8: Isoconversion Controls and Handler
    IsoconversionControls().render()
    IsoconversionHandler().handle_isoconversion()

    # ------------------------------------------------------------------ #
    # STEP 7: Activation Energy                                            #
    # ------------------------------------------------------------------ #

    ActivationEnergyControls().render()
    ae_handler = ActivationEnergyHandler()
    if ae_handler.setup():
        ae_handler.handle_activation_energy()

    # ------------------------------------------------------------------ #
    # STEP 8: Compensation Effect (Pre-exponential Factor)                 #
    # ------------------------------------------------------------------ #

    CompensationEffectControls().render()
    CompensationEffectHandler().handle_compensation_effect()

    # ------------------------------------------------------------------ #
    # STEP 9: Reaction Model Reconstruction — g(alpha)                    #
    # ------------------------------------------------------------------ #

    ReconstructionControls().render()
    ReconstructionHandler().handle_reconstruction()

    # ------------------------------------------------------------------ #
    # STEP 10: Kinetic Predictions                                         #
    # ------------------------------------------------------------------ #

    PredictionControls().render()
    PredictionHandler().handle_predictions()


if __name__ == "__main__":
    main()
