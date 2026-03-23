"""
Session state management utilities.
"""

import streamlit as st
from typing import Any
from src.config import SESS_FILE_PATHS


class SessionManager:
    """Centralized management of Streamlit session state."""

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        return st.session_state.get(key, default)

    @staticmethod
    def set(key: str, value: Any) -> None:
        st.session_state[key] = value

    @staticmethod
    def delete(key: str) -> None:
        if key in st.session_state:
            del st.session_state[key]

    @staticmethod
    def delete_multiple(keys: list) -> None:
        """
        Delete multiple keys from session state.
        
        Args:
            keys (list): List of session key names to delete.
        """
        for key in keys:
            SessionManager.delete(key)

    @staticmethod
    def clear_extraction_state() -> None:
        """Clear all extraction-related session state."""
        keys_to_clear = [
            'data_extractor', 'Bnum', 'T0num', 'conversion_ready',
            'last_conversion_figure', SESS_FILE_PATHS, 'extract_data_clicked',
            'conversion_ranges', 'plotly_plotters'
        ]
        SessionManager.delete_multiple(keys_to_clear)

    @staticmethod
    def is_conversion_ready() -> bool:
        """Check if conversion data is ready."""
        return SessionManager.get('conversion_ready', False)

    @staticmethod
    def get_file_paths() -> list:
        """Get current file paths from session state."""
        return SessionManager.get(SESS_FILE_PATHS, [])

    @staticmethod
    def set_file_paths(paths: list, source: str = 'default', folder: str = '') -> None:
        """
        Set file paths and metadata in session state.
        
        Args:
            paths (list): List of file paths.
            source (str): Source of files ('default' or 'upload').
            folder (str): Folder path if from default files.
        """
        SessionManager.set(SESS_FILE_PATHS, paths)
        SessionManager.set('file_paths_source', source)
        if folder:
            SessionManager.set('file_paths_folder', folder)
