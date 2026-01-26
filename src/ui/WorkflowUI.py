"""
Workflow UI Components

This module contains all Streamlit UI components that trigger program workflows,
including file selection, validation, data extraction, plotting, and conversion
analysis interfaces.

Responsibilities:
- File upload and default dataset selection UI
- File validation feedback and display
- Data extraction workflow controls
- Interactive plot generation and manipulation
- Conversion analysis setup and execution
"""

import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

import streamlit as st
import pandas as pd

from src.config import (
    DEFAULT_MAX_FILES,
    DEFAULT_MIN_FILES,
    DEFAULT_FILES_DIR,
    DEFAULT_FILE_TYPES,
    PLOT_X_DATA_OPTIONS,
    PLOT_Y_DATA_OPTIONS,
    PLOT_X_UNITS,
    PLOT_Y_UNITS,
    DEFAULT_ISO_DA,
)
from src.utils.FileValidator import FileValidator
from src.utils.SessionManager import SessionManager
from src.core.conversion_manager import ConversionManager
from src.ui.PlotlyPlotter import PlotlyPlotter
from src.ui.plot_manager import PlotManager


class WorkflowUI:
    """
    Orchestrates all user interface components for data processing workflow.
    
    This class manages:
    - File source selection (upload vs. default datasets)
    - File validation and preview
    - Data extraction triggering
    - Interactive plot display
    - Conversion analysis workflow
    """

    def __init__(self):
        """Initialize WorkflowUI with default configuration."""
        self.default_dir = str(DEFAULT_FILES_DIR)
        self.file_types = DEFAULT_FILE_TYPES
        self.max_files = DEFAULT_MAX_FILES
        self.min_files = DEFAULT_MIN_FILES

    def load_default_files(self, folder: Optional[str] = None) -> List[str]:
        """
        Load default files from the specified directory.

        Args:
            folder: Optional subfolder name. If None, lists all files in default_dir.

        Returns:
            List of file paths found.
        """
        if folder:
            target_dir = os.path.join(self.default_dir, folder)
        else:
            target_dir = self.default_dir

        if os.path.exists(target_dir) and os.path.isdir(target_dir):
            default_files = [
                os.path.join(target_dir, f)
                for f in os.listdir(target_dir)
                if f.endswith(tuple(self.file_types))
            ]
            if default_files:
                st.info(f"Loaded {len(default_files)} default file(s) from: {target_dir}")
            else:
                st.warning(f"No files found in: {target_dir}")
            return default_files
        else:
            st.error(f"Directory '{target_dir}' does not exist or is not accessible.")
            return []

    def upload_files_widget(self) -> List[str]:
        """
        Create file uploader widget and return paths to uploaded files.

        Returns:
            List of file paths saved to temporary directory.
        """
        uploaded_files = st.file_uploader(
            f"Choose CSV files (minimum {self.min_files}, maximum {self.max_files})",
            type=self.file_types,
            accept_multiple_files=True,
            key="workflow_file_uploader",
        )

        file_paths = []
        if uploaded_files:
            for uploaded_file in uploaded_files:
                temp_path = os.path.join("/tmp", uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(temp_path)

        return file_paths

    def choose_input_source(self) -> Optional[List[str]]:
        """
        Display toggle between uploading files and selecting default dataset.

        Returns:
            List of selected file paths or None if no selection made.
        """
        st.subheader("Data Source Selection")

        choice = st.radio(
            "Data source:",
            ["Select default dataset", "Upload files"],
            index=0,
            key="workflow_input_source_radio",
        )

        if choice == "Select default dataset":
            return self._display_default_dataset_selector()
        else:
            return self._display_file_uploader()

    def _display_default_dataset_selector(self) -> Optional[List[str]]:
        """
        Display selector for default datasets with folder and file selection.

        Returns:
            List of selected file paths or None.
        """
        if not os.path.exists(self.default_dir) or not os.path.isdir(self.default_dir):
            st.error(f"Default directory '{self.default_dir}' does not exist.")
            return None

        # List subdirectories
        subdirs = [
            d
            for d in os.listdir(self.default_dir)
            if os.path.isdir(os.path.join(self.default_dir, d))
        ]

        if not subdirs:
            st.warning("No default datasets found.")
            return None

        # Folder selection
        chosen_folder = st.selectbox("Choose default folder:", subdirs, index=0)
        folder_path = os.path.join(self.default_dir, chosen_folder)

        # File selection
        default_files = [
            f for f in os.listdir(folder_path) if f.endswith(tuple(self.file_types))
        ]

        if not default_files:
            st.warning("No files found in the selected folder.")
            return None

        chosen = st.multiselect(
            "Choose files to use:",
            default_files,
            default=default_files,
            key="workflow_default_files_select",
        )

        if chosen:
            chosen_paths = [os.path.join(folder_path, c) for c in chosen]
            SessionManager.set("file_paths", chosen_paths)
            SessionManager.set("file_paths_source", "default")
            SessionManager.set("file_paths_folder", folder_path)
            st.success(f"Selected {len(chosen_paths)} file(s) from '{chosen_folder}'")
            return chosen_paths
        else:
            st.info("No files selected.")
            return None

    def _display_file_uploader(self) -> Optional[List[str]]:
        """
        Display file uploader widget and return paths.

        Returns:
            List of uploaded file paths or None.
        """
        file_paths = self.upload_files_widget()
        if file_paths:
            SessionManager.set("file_paths", file_paths)
            SessionManager.set("file_paths_source", "upload")
            return file_paths
        return None

    def verify_file_count(self, file_paths: Optional[List[str]] = None) -> bool:
        """
        Verify file count meets requirements.

        Args:
            file_paths: List of file paths. If None, retrieves from session.

        Returns:
            True if count is valid, False otherwise.
        """
        if file_paths is None:
            file_paths = SessionManager.get("file_paths", [])

        num_files = len(file_paths)

        if num_files < self.min_files:
            st.error(
                f"Please upload at least {self.min_files} CSV files. "
                f"Currently: {num_files}"
            )
            return False
        elif num_files > self.max_files:
            st.error(
                f"Please upload at most {self.max_files} CSV files. "
                f"Currently: {num_files}"
            )
            return False
        else:
            st.success(f" {num_files} file(s) ready")
            return True

    def verify_file_structure(self, file_paths: Optional[List[str]] = None) -> Tuple[List[pd.DataFrame], List[Tuple[str, str]]]:
        """
        Validate file structure (columns, encoding).

        Args:
            file_paths: List of file paths. If None, retrieves from session.

        Returns:
            Tuple of (valid_dataframes, invalid_file_errors).
        """
        if file_paths is None:
            file_paths = SessionManager.get("file_paths", [])

        if not file_paths:
            st.error("No files to validate.")
            return [], []

        valid_files, invalid_files = FileValidator.validate_files(file_paths)

        # Display validation results
        if invalid_files:
            st.warning(f"{len(invalid_files)} file(s) could not be processed:")
            for filename, error_msg in invalid_files:
                st.write(f"  • {Path(filename).name}: {error_msg}")

        if valid_files:
            st.success(f" {len(valid_files)} valid file(s) loaded")

        return valid_files, invalid_files

    def display_file_preview(self, valid_files: List[pd.DataFrame], file_paths: List[str]) -> None:
        """
        Display preview of validated files in tabs.

        Args:
            valid_files: List of validated DataFrames.
            file_paths: List of corresponding file paths.
        """
        if not valid_files:
            st.warning("No valid files to display.")
            return

        st.header("Files Preview")

        # Create tabs for each valid file
        tab_names = [f"File {i + 1}: {Path(file_paths[i]).name}" for i in range(len(valid_files))]
        tabs = st.tabs(tab_names)

        for tab, valid_file in zip(tabs, valid_files):
            with tab:
                st.dataframe(valid_file, use_container_width=True)

    def display_extraction_controls(self) -> None:
        """
        Display Reset and Extract Data buttons for data extraction workflow.
        """
        st.divider()
        st.subheader("Data Extraction")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Reset All", type="secondary", key="workflow_reset_btn"):
                SessionManager.clear_extraction_state()
                st.success("Application reset. Reload the page to start fresh.")

        with col2:
            if st.button("Extract Data", type="primary", key="workflow_extract_btn"):
                SessionManager.set("extract_data_clicked", True)

    def handle_data_extraction(self) -> bool:
        """
        Handle data extraction workflow when triggered.

        Returns:
            True if extraction was successful, False otherwise.
        """
        if not SessionManager.get("extract_data_clicked"):
            return False

        file_paths = SessionManager.get("file_paths", [])
        if not file_paths:
            st.error("No files available for extraction.")
            return False

        st.info("Extracting data from files...")

        try:
            # Import here to avoid circular imports
            from picnick_dev import DataExtraction as DE

            data_extractor = DE()
            Bnum, T0num = data_extractor.read_files(file_paths)

            # Store extraction results in session
            SessionManager.set("data_extractor", data_extractor)
            SessionManager.set("Bnum", Bnum)
            SessionManager.set("T0num", T0num)
            SessionManager.set("conversion_ready", True)

            st.success("Data extraction completed successfully")
            st.write(f"Processed files: {', '.join(Path(f).name for f in file_paths)}")

            return True

        except UnicodeDecodeError:
            st.warning("Encoding error detected. Attempting recovery...")
            return self._handle_encoding_retry(file_paths)

        except Exception as e:
            st.error(f"Error during extraction: {str(e)}")
            return False

    def _handle_encoding_retry(self, file_paths: List[str]) -> bool:
        """
        Handle encoding errors by re-reading with safe encoding.

        Args:
            file_paths: Original file paths.

        Returns:
            True if retry successful, False otherwise.
        """
        try:
            from picnick_dev import DataExtraction as DE

            temp_paths = []
            with tempfile.TemporaryDirectory() as temp_dir:
                for f in file_paths:
                    try:
                        df = FileValidator.safe_read_csv(f)
                        # Save to temp file as utf-8
                        temp_path = os.path.join(temp_dir, Path(f).name)
                        df.to_csv(temp_path, index=False, encoding="utf-8")
                        temp_paths.append(temp_path)
                    except Exception as e:
                        st.error(f"Failed to re-encode {Path(f).name}: {str(e)}")

                if temp_paths:
                    data_extractor = DE()
                    Bnum, T0num = data_extractor.read_files(temp_paths)

                    SessionManager.set("data_extractor", data_extractor)
                    SessionManager.set("Bnum", Bnum)
                    SessionManager.set("T0num", T0num)
                    SessionManager.set("conversion_ready", True)

                    st.success("Files recovered with safe encoding")
                    return True
                else:
                    st.error("Could not process any files with safe encoding.")
                    return False

        except Exception as e:
            st.error(f"Encoding recovery failed: {str(e)}")
            return False

    def display_plots(self) -> None:
        """
        Display all available plot combinations with interactive controls.
        """
        data_extractor = SessionManager.get("data_extractor")
        if data_extractor is None:
            st.info("Extract data first to display plots.")
            return

        st.header("Interactive Plots")

        plot_manager = PlotManager(data_extractor)
        plot_tabs = plot_manager.generate_plot_tabs()

        tabs = st.tabs(plot_tabs)

        for idx, tab in enumerate(tabs):
            with tab:
                try:
                    x_data, x_unit, y_data, y_unit = plot_manager.parse_tab_name(
                        plot_tabs[idx]
                    )

                    # Create plot
                    plotter = plot_manager.create_plot(
                        x_data, y_data, x_unit, y_unit
                    )

                    if plotter is None:
                        st.error(f"Failed to create plot for {plot_tabs[idx]}")
                        continue

                    # Display plot
                    placeholder = st.empty()
                    plotter.show(container=placeholder)

                    # Store plotter in session for later manipulation
                    plotters_dict = SessionManager.get("plotly_plotters", {})
                    plotters_dict[idx] = {"plotter": plotter, "placeholder": placeholder}
                    SessionManager.set("plotly_plotters", plotters_dict)

                    # Display range controls for interactive adjustment
                    plot_manager.display_plot_range_controls(
                        idx, plotter, placeholder
                    )

                except KeyError as e:
                    st.error(f"Invalid plot combination: {str(e)}")
                except Exception as e:
                    st.error(f"Error creating plot: {str(e)}")

    def display_conversion_controls(self) -> None:
        """
        Display conversion analysis controls and execution button.
        """
        if not SessionManager.get("conversion_ready"):
            st.info("Conversion unavailable. Extract data first.")
            return

        st.divider()
        st.header("Conversion Analysis")

        st.subheader("Configure Analysis Parameters")

        Bnum = SessionManager.get("Bnum")
        if Bnum is not None:
            num_datasets = len(Bnum)
            st.write(f"Number of datasets: **{num_datasets}**")

            # Optional: Display range configuration interface
            if st.button("Configure Temperature Ranges", key="configure_ranges_btn"):
                st.info("Range configuration UI would be displayed here")

        if st.button("Run Conversion Analysis", type="primary", key="run_conversion_btn"):
            self.handle_conversion_analysis()

    def handle_conversion_analysis(self) -> None:
        """
        Execute conversion and isoconversion analysis.
        """
        data_extractor = SessionManager.get("data_extractor")
        Bnum = SessionManager.get("Bnum")

        if data_extractor is None or Bnum is None:
            st.error("No extracted data available for conversion.")
            return

        try:
            st.info("Running conversion analysis...")

            conversion_manager = ConversionManager(data_extractor)

            # Get temperature ranges
            ranges = SessionManager.get("conversion_ranges")
            if ranges and len(ranges) == len(Bnum):
                Ti_list = [r[0] for r in ranges]
                Tf_list = [r[1] for r in ranges]
            else:
                # Use default: first to last temperature for each dataset
                Ti_list = [
                    data_extractor.DFlis[k]["Temperature [K]"].values[0]
                    for k in range(len(Bnum))
                ]
                Tf_list = [
                    data_extractor.DFlis[k]["Temperature [K]"].values[-1]
                    for k in range(len(Bnum))
                ]

            # Execute conversion
            conversion_figure, iso_tables = conversion_manager.run_conversion(
                Ti_list, Tf_list
            )

            if conversion_figure is None:
                st.error("Conversion calculation failed.")
                return

            st.success("Conversion analysis completed")

            # Display results
            col1, col2 = st.columns([2, 1])

            with col1:
                st.pyplot(conversion_figure)

            with col2:
                st.subheader("Analysis Summary")
                st.write(f"Datasets analyzed: **{len(Bnum)}**")
                st.write(f"Temperature ranges:")
                for i, (ti, tf) in enumerate(zip(Ti_list, Tf_list)):
                    st.write(f"  • Dataset {i + 1}: {ti:.1f} K → {tf:.1f} K")

            # Display isoconversion tables if available
            if iso_tables is not None:
                st.subheader("Isoconversion Data")
                st.info("Isoconversion tables would be displayed here")

        except Exception as e:
            st.error(f"Error during conversion analysis: {str(e)}")
