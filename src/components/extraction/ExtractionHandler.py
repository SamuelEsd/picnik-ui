"""
Extraction Handler Component

Manages data extraction workflow and encoding retry logic.
"""

import os
import tempfile
from pathlib import Path
from typing import List

import streamlit as st

from src.utils.FileValidator import FileValidator
from src.utils.SessionManager import SessionManager
from src.config import (
    SESS_FILE_PATHS, SESS_BNUM, SESS_DATA_EXTRACTOR,
    SESS_T0_NUM, SESS_CONVERSION_READY, SESS_EXTRACT_CLICKED,
)


class ExtractionHandler:
    """Component for handling data extraction."""

    def handle_extraction(self) -> bool:
        """
        Handle data extraction workflow when triggered.

        Returns:
            True if extraction was successful, False otherwise.
        """
        if not SessionManager.get(SESS_EXTRACT_CLICKED):
            return False

        SessionManager.set(SESS_EXTRACT_CLICKED, False)
        file_paths = SessionManager.get(SESS_FILE_PATHS, [])
        if not file_paths:
            st.error("No files available for extraction.")
            return False

        st.info("Extracting data from files...")

        try:
            SessionManager.clear_downstream_from("extraction")
            # Import here to avoid circular imports
            from picnick_dev import DataExtraction as DE

            file_paths = self._sort_files_by_beta(file_paths)

            data_extractor = DE()
            # summary=False: the UI provides its own interactive plots via PlotViewer.
            # The default summary=True generates a matplotlib figure with plt.show()
            # that is not rendered in Streamlit and pollutes the matplotlib figure state.
            Bnum, T0num = data_extractor.read_files(file_paths, summary=False)

            # Store extraction results in session
            SessionManager.set(SESS_DATA_EXTRACTOR, data_extractor)
            SessionManager.set(SESS_BNUM, Bnum)
            SessionManager.set(SESS_T0_NUM, T0num)
            SessionManager.set(SESS_CONVERSION_READY, True)

            st.success("Data extraction completed successfully")
            st.write(f"Processed files: {', '.join(Path(f).name for f in file_paths)}")

            return True

        except UnicodeDecodeError:
            st.warning("Encoding error detected. Attempting recovery...")
            return self._handle_encoding_retry(file_paths)

        except Exception as e:
            st.error(f"Error during extraction: {str(e)}")
            return False

    def _estimate_beta(self, filepath: str) -> float:
        """Estimate β (K/min) from a file by computing the slope of T vs t."""
        try:
            df = FileValidator.safe_read_csv(filepath)
            if len(df.columns) < 2:
                return 0.0
            t = list(df.iloc[:, 0].astype(float))
            T = list(df.iloc[:, 1].astype(float))
            n = len(t)
            if n < 2:
                return 0.0
            mean_t = sum(t) / n
            mean_T = sum(T) / n
            num = sum((ti - mean_t) * (Ti - mean_T) for ti, Ti in zip(t, T))
            den = sum((ti - mean_t) ** 2 for ti in t)
            return num / den if den != 0 else 0.0
        except Exception:
            return 0.0

    def _sort_files_by_beta(self, file_paths: List[str]) -> List[str]:
        """Return file_paths sorted by ascending estimated heating rate β."""
        return sorted(file_paths, key=self._estimate_beta)

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
                    Bnum, T0num = data_extractor.read_files(temp_paths, summary=False)

                    SessionManager.set(SESS_DATA_EXTRACTOR, data_extractor)
                    SessionManager.set(SESS_BNUM, Bnum)
                    SessionManager.set(SESS_T0_NUM, T0num)
                    SessionManager.set(SESS_CONVERSION_READY, True)

                    st.success("Files recovered with safe encoding")
                    return True
                else:
                    st.error("Could not process any files with safe encoding.")
                    return False

        except Exception as e:
            st.error(f"Encoding recovery failed: {str(e)}")
            return False
