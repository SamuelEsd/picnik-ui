"""
Default Dataset Selector Component

Handles selection of default datasets from predefined folders.
"""

import os
import re
from pathlib import Path
from typing import List, Optional

import streamlit as st

from src.config import DEFAULT_FILES_DIR, DEFAULT_FILE_TYPES, SESS_FILE_PATHS
from src.utils.SessionManager import SessionManager


class DefaultDatasetSelector:
    """Component for selecting default datasets."""

    def __init__(self):
        """Initialize DefaultDatasetSelector."""
        self.default_dir = str(DEFAULT_FILES_DIR)
        self.file_types = DEFAULT_FILE_TYPES

    def render(self) -> Optional[List[str]]:
        """
        Render the default dataset selector component.

        Returns:
            List of selected file paths or None.
        """
        if not os.path.exists(self.default_dir) or not os.path.isdir(self.default_dir):
            st.error(f"Default directory '{self.default_dir}' does not exist.")
            return None

        # List subdirectories
        subdirs = self._get_subdirectories()
        if not subdirs:
            st.warning("No default datasets found.")
            return None

        # Folder selection
        chosen_folder = st.selectbox("Choose default folder:", subdirs, index=0)
        folder_path = os.path.join(self.default_dir, chosen_folder)

        # File selection
        default_files = self._get_available_files(folder_path)
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
            return self._process_selected_files(chosen, folder_path, chosen_folder)
        else:
            st.info("No files selected.")
            return None

    def _get_subdirectories(self) -> List[str]:
        """
        Get list of subdirectories in default directory.

        Returns:
            List of subdirectory names.
        """
        return [
            d
            for d in os.listdir(self.default_dir)
            if os.path.isdir(os.path.join(self.default_dir, d))
        ]

    def _get_available_files(self, folder_path: str) -> List[str]:
        """
        Get available files in a folder.

        Args:
            folder_path: Path to the folder.

        Returns:
            List of file names matching file types.
        """
        files = [f for f in os.listdir(folder_path) if f.endswith(tuple(self.file_types))]
        return sorted(files, key=lambda f: int(m.group()) if (m := re.search(r'\d+', f)) else float('inf'))

    def _process_selected_files(
        self, chosen: List[str], folder_path: str, folder_name: str
    ) -> List[str]:
        """
        Process and store selected files.

        Args:
            chosen: List of chosen file names.
            folder_path: Path to the folder.
            folder_name: Name of the folder.

        Returns:
            List of full file paths.
        """
        chosen_paths = [os.path.join(folder_path, c) for c in chosen]
        SessionManager.set(SESS_FILE_PATHS, chosen_paths)
        SessionManager.set("file_paths_source", "default")
        SessionManager.set("file_paths_folder", folder_path)
        st.success(f"Selected {len(chosen_paths)} file(s) from '{folder_name}'")
        return chosen_paths
