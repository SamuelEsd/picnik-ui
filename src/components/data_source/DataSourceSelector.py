"""
Data Source Selector Component

Allows users to choose between uploading files or selecting default datasets.
"""

import os
import re
from pathlib import Path
from typing import List, Optional

import streamlit as st

from src.config import DEFAULT_FILES_DIR, DEFAULT_FILE_TYPES, DEFAULT_MIN_FILES, DEFAULT_MAX_FILES, SESS_FILE_PATHS, SESS_FILE_SOURCE
from src.utils.SessionManager import SessionManager
from .DefaultDatasetSelector import DefaultDatasetSelector


class DataSourceSelector:
    """Component for selecting data source (upload or default)."""

    def __init__(self):
        """Initialize DataSourceSelector."""
        self.default_dir = str(DEFAULT_FILES_DIR)
        self.file_types = DEFAULT_FILE_TYPES
        self.min_files = DEFAULT_MIN_FILES
        self.max_files = DEFAULT_MAX_FILES
        self.default_dataset_selector = DefaultDatasetSelector()

    def render(self) -> Optional[List[str]]:
        """
        Render the data source selector component.

        Returns:
            List of selected file paths or None if no selection made.
        """
        st.divider()
        st.subheader("Step 1: Data Source Selection")

        choice = st.radio(
            "Data source:",
            ["Select default dataset", "Upload files"],
            index=0,
            key="workflow_input_source_radio",
        )

        if choice == "Select default dataset":
            return self.default_dataset_selector.render()
        else:
            return self._render_file_uploader()

    def _render_file_uploader(self) -> Optional[List[str]]:
        """
        Render file uploader widget.

        Returns:
            List of uploaded file paths or None.
        """
        file_paths = self._upload_files_widget()
        if file_paths:
            st.session_state[SESS_FILE_PATHS] = file_paths
            st.session_state[SESS_FILE_SOURCE] = "upload"
            return file_paths
        return None

    def _upload_files_widget(self) -> List[str]:
        """
        Create file uploader widget.

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
            upload_dir = SessionManager.get_upload_dir()
            for uploaded_file in uploaded_files:
                temp_path = os.path.join(upload_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(temp_path)

        return sorted(file_paths, key=lambda p: int(m.group()) if (m := re.search(r'\d+', os.path.basename(p))) else float('inf'))
