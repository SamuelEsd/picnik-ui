"""
File Count Validator Component

Validates that file count meets minimum and maximum requirements.
"""

from typing import List, Optional

import streamlit as st

from src.config import DEFAULT_MIN_FILES, DEFAULT_MAX_FILES, SESS_FILE_PATHS
from src.utils.SessionManager import SessionManager


class FileCountValidator:
    """Component for validating file count."""

    def __init__(self, min_files: int = DEFAULT_MIN_FILES, max_files: int = DEFAULT_MAX_FILES):
        """
        Initialize FileCountValidator.

        Args:
            min_files: Minimum number of files allowed.
            max_files: Maximum number of files allowed.
        """
        self.min_files = min_files
        self.max_files = max_files

    def validate(self, file_paths: Optional[List[str]] = None) -> bool:
        """
        Validate file count meets requirements.

        Args:
            file_paths: List of file paths. If None, retrieves from session.

        Returns:
            True if count is valid, False otherwise.
        """
        if file_paths is None:
            file_paths = SessionManager.get(SESS_FILE_PATHS, [])

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
            st.success(f"✓ {num_files} file(s) ready")
            return True
