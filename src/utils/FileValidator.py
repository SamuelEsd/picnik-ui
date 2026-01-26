"""
File validation utilities for the data processing pipeline.
"""

import pandas as pd
from typing import List, Tuple
from src.config import EXPECTED_COLUMNS, SUPPORTED_ENCODINGS


class FileValidator:
    """Handles CSV file validation and reading with encoding detection."""

    @staticmethod
    def safe_read_csv(filepath: str) -> pd.DataFrame:
        """
        Safely read a CSV file with automatic encoding detection.
        
        Tries encodings in order: UTF-8-SIG, then UTF-16LE.
        
        Args:
            filepath (str): Path to the CSV file.
            
        Returns:
            pd.DataFrame: The loaded DataFrame.
            
        Raises:
            Exception: If the file cannot be read with any supported encoding.
        """
        for encoding in SUPPORTED_ENCODINGS:
            try:
                return pd.read_csv(filepath, encoding=encoding)
            except UnicodeDecodeError:
                continue
        
        raise Exception(
            f"Failed to read {filepath} with any supported encoding: {SUPPORTED_ENCODINGS}"
        )

    @staticmethod
    def validate_dataframe_columns(df: pd.DataFrame, expected_cols: int = EXPECTED_COLUMNS) -> bool:
        """
        Validate that a DataFrame has the expected number of columns.
        
        Args:
            df (pd.DataFrame): The DataFrame to validate.
            expected_cols (int): The expected number of columns.
            
        Returns:
            bool: True if column count matches, False otherwise.
        """
        return len(df.columns) == expected_cols

    @staticmethod
    def validate_files(file_paths: List[str]) -> Tuple[List[pd.DataFrame], List[Tuple[str, str]]]:
        """
        Validate multiple files for correct format and column count.
        
        Args:
            file_paths (List[str]): List of file paths to validate.
            
        Returns:
            Tuple containing:
                - List[pd.DataFrame]: List of successfully loaded DataFrames
                - List[Tuple[str, str]]: List of (filepath, error_reason) tuples for invalid files
        """
        valid_files = []
        invalid_files = []

        for filepath in file_paths:
            try:
                df = FileValidator.safe_read_csv(filepath)
            except Exception as e:
                invalid_files.append((filepath, f"Unreadable: {str(e)}"))
                continue

            if not FileValidator.validate_dataframe_columns(df):
                invalid_files.append((filepath, f"Expected {EXPECTED_COLUMNS} columns, got {len(df.columns)}"))
            else:
                valid_files.append(df)

        return valid_files, invalid_files
