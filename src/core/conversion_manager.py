"""
Conversion and isoconversion calculations management.
"""

import streamlit as st
import tempfile
import os
from typing import List, Tuple, Optional
from src.utils.FileValidator import FileValidator
from src.utils.SessionManager import SessionManager
from src.config import DEFAULT_ISO_DA


class ConversionManager:
    """Manages conversion and isoconversion calculations."""

    def __init__(self, data_extractor):
        """
        Initialize ConversionManager.
        
        Args:
            data_extractor: DataExtraction instance for calculations.
        """
        self.data_extractor = data_extractor

    def get_temperature_ranges(self) -> Optional[List[Tuple[float, float]]]:
        """
        Get temperature ranges for conversion.
        
        Uses stored ranges if available, otherwise extracts from data.
        
        Returns:
            List of (Ti, Tf) tuples or None if data unavailable.
        """
        Bnum = SessionManager.get('Bnum')
        if Bnum is None:
            return None

        ranges = SessionManager.get('conversion_ranges')
        if ranges and len(ranges) == len(Bnum):
            return ranges

        # Extract from data
        try:
            Ti_list = [self.data_extractor.DFlis[k]['Temperature [K]'].values[0] for k in range(len(Bnum))]
            Tf_list = [self.data_extractor.DFlis[k]['Temperature [K]'].values[-1] for k in range(len(Bnum))]
            return list(zip(Ti_list, Tf_list))
        except Exception:
            return None

    def run_conversion(self, Ti_list: List[float], Tf_list: List[float]):
        """
        Execute conversion and isoconversion calculations.
        
        Args:
            Ti_list (List[float]): Initial temperatures for each dataset.
            Tf_list (List[float]): Final temperatures for each dataset.
            
        Returns:
            Tuple of (conversion_figure, isoTables_num) or (None, None) on error.
        """
        try:
            conversion_figure = self.data_extractor.Conversion(Ti_list, Tf_list)
            isoTables_num = self.data_extractor.Isoconversion(d_a=DEFAULT_ISO_DA)
            return conversion_figure, isoTables_num
        except Exception as e:
            st.error(f"Error during conversion: {str(e)}")
            return None, None

    def handle_encoding_retry(self, file_paths: List[str]) -> Optional[List[str]]:
        """
        Retry reading files with safe encoding if initial read fails.
        
        Args:
            file_paths (List[str]): Original file paths.
            
        Returns:
            List of re-encoded temp file paths or None on failure.
        """
        try:
            temp_paths = []
            for f in file_paths:
                try:
                    df = FileValidator.safe_read_csv(f)
                    # Save to temp file as UTF-8
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w')
                    df.to_csv(tmp.name, index=False, encoding='utf-8')
                    temp_paths.append(tmp.name)
                except Exception as e:
                    st.error(f"Failed to re-encode {f}: {str(e)}")
                    return None

            if temp_paths:
                st.info("Files reloaded with safe encoding and re-encoded to utf-8.")
                return temp_paths
            return None
        except Exception as e:
            st.error(f"Encoding retry failed: {str(e)}")
            return None

    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """
        Clean up temporary files.
        
        Args:
            file_paths (List[str]): Paths to temporary files to remove.
        """
        for filepath in file_paths:
            try:
                if os.path.exists(filepath) and filepath.startswith(tempfile.gettempdir()):
                    os.remove(filepath)
            except Exception:
                pass

    def display_ranges_summary(self) -> None:
        """Display a summary of selected temperature ranges."""
        Bnum = SessionManager.get('Bnum')
        ranges = SessionManager.get('conversion_ranges')

        if ranges and Bnum:
            st.write("**Selected Temperature Ranges:**")
            for idx, (min_temp, max_temp) in enumerate(ranges):
                st.write(f"  Dataset {idx + 1}: {min_temp:.2f} K → {max_temp:.2f} K")
        else:
            st.info("No custom ranges set. Default first-to-last temperature will be used.")
