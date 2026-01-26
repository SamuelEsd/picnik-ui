"""
Session state management utilities.
"""

import streamlit as st
from typing import Any, Dict
from src.config import SESSION_KEYS


class SessionManager:
    """Centralized management of Streamlit session state."""

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get a value from session state.
        
        Args:
            key (str): The session key name or SESSION_KEYS reference.
            default (Any): Default value if key not found.
            
        Returns:
            Any: The value from session state or default.
        """
        session_key = SESSION_KEYS.get(key, key)
        return st.session_state.get(session_key, default)

    @staticmethod
    def set(key: str, value: Any) -> None:
        """
        Set a value in session state.
        
        Args:
            key (str): The session key name or SESSION_KEYS reference.
            value (Any): The value to store.
        """
        session_key = SESSION_KEYS.get(key, key)
        st.session_state[session_key] = value

    @staticmethod
    def delete(key: str) -> None:
        """
        Delete a key from session state if it exists.
        
        Args:
            key (str): The session key name or SESSION_KEYS reference.
        """
        session_key = SESSION_KEYS.get(key, key)
        if session_key in st.session_state:
            del st.session_state[session_key]

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
            'last_conversion_figure', 'file_paths', 'extract_data_clicked',
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
        return SessionManager.get('file_paths', [])

    @staticmethod
    def set_file_paths(paths: list, source: str = 'default', folder: str = '') -> None:
        """
        Set file paths and metadata in session state.
        
        Args:
            paths (list): List of file paths.
            source (str): Source of files ('default' or 'upload').
            folder (str): Folder path if from default files.
        """
        SessionManager.set('file_paths', paths)
        SessionManager.set('file_paths_source', source)
        if folder:
            SessionManager.set('file_paths_folder', folder)
