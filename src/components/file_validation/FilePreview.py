"""
File Preview Component

Displays a preview of validated files in tabs.
"""

from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st


class FilePreview:
    """Component for displaying file previews."""

    def render(self, valid_files: List[pd.DataFrame], file_paths: List[str]) -> None:
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
        tab_names = [
            f"File {i + 1}: {Path(file_paths[i]).name}" for i in range(len(valid_files))
        ]
        tabs = st.tabs(tab_names)

        for tab, valid_file in zip(tabs, valid_files):
            with tab:
                st.dataframe(valid_file, width='stretch')
