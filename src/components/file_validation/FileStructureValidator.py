"""
File Structure Validator Component

Validates file structure (columns, encoding, format).
"""

from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd
import streamlit as st

from src.utils.FileValidator import FileValidator
from src.utils.SessionManager import SessionManager
from src.config import SESS_FILE_PATHS


class FileStructureValidator:
    """Component for validating file structure."""

    def validate(
        self, file_paths: Optional[List[str]] = None
    ) -> Tuple[List[pd.DataFrame], List[Tuple[str, str]]]:
        """
        Validate file structure (columns, encoding).

        Args:
            file_paths: List of file paths. If None, retrieves from session.

        Returns:
            Tuple of (valid_dataframes, invalid_file_errors).
        """
        if file_paths is None:
            file_paths = SessionManager.get(SESS_FILE_PATHS, [])

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
            st.success(f"✓ {len(valid_files)} valid file(s) loaded")

        return valid_files, invalid_files
