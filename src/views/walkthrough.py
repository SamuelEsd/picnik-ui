"""
Walkthrough Tutorial View - Using Component-Based Architecture

This view demonstrates an interactive tutorial for learning how to use
the thermal analysis tool with modular components.
"""

import streamlit as st
import base64
from pathlib import Path

from src.config import APP_TITLE, RESOURCES_DIR
from src.components.data_source import DataSourceSelector
from src.components.file_validation import (
    FileCountValidator,
    FileStructureValidator,
    FilePreview,
)


def main():
    """Main walkthrough tutorial flow using modular components."""
    # Page configuration
    st.set_page_config(layout="wide", initial_sidebar_state="expanded")

    # Set page title
    st.title(f"{APP_TITLE} - Tutorial")

    # Step 1: Introduction
    st.header("Step 1: Download Example Files")
    st.markdown(
        """
        <span style='font-weight: bold;'>
        Learn how to download and prepare your thermal analysis data files
        </span>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        1. Navigate to the resources folder in the project
        2. Download the example CSV files from `resources/default_files/`
        3. Files must have exactly 3 columns: Temperature, TG, and DTG
        4. Ensure CSV encoding is UTF-8 or UTF-16 LE for compatibility
        """
    )

    # Display example image if available
    gif_path = RESOURCES_DIR / "download_example_files.gif"
    if gif_path.exists():
        with open(gif_path, "rb") as file_:
            contents = file_.read()
            data_url = base64.b64encode(contents).decode("utf-8")
            st.markdown(
                f'<img src="data:image/gif;base64,{data_url}" alt="example gif">',
                unsafe_allow_html=True,
            )
    else:
        st.info("Example GIF not found. Continue to Step 2 to upload your files.")

    # Step 2: File Upload and Validation
    st.header("Step 2: Upload Your Data Files")
    st.markdown(
        f"""
        Upload your CSV files for thermal analysis. 
        Each file must contain exactly **3 columns**.
        """
    )

    # Component 1: Data Source Selection
    data_source_selector = DataSourceSelector()
    file_paths = data_source_selector.render()
    if not file_paths:
        st.info("Please select files to proceed.")
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

    # Step 3: Next Steps
    st.header("Step 3: Proceed to Analysis")
    st.markdown(
        """
        Your data has been validated and is ready for analysis!
        
        Next steps:
        1. Go to the **Tool** page from the navigation menu
        2. Click "Extract Data" to process the files
        3. Visualize and analyze your thermal data with interactive plots
        4. Run conversion and isoconversion analysis
        """
    )

    st.success("Your files are ready! Navigate to the Tool page to continue with data analysis.")


if __name__ == "__main__":
    main()
