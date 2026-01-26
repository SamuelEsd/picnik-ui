"""
Application configuration and constants.

This module centralizes all application-level configuration,
including file paths, validation rules, UI settings, and constants.
"""

import os
from pathlib import Path
from typing import Dict, List

# ============================================================================
# PROJECT PATHS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
RESOURCES_DIR = PROJECT_ROOT / "resources"
DEFAULT_FILES_DIR = RESOURCES_DIR / "default_files"

# ============================================================================
# FILE UPLOAD CONFIGURATION
# ============================================================================
DEFAULT_FILE_TYPES: List[str] = ['csv']
DEFAULT_MAX_FILES: int = 20
DEFAULT_MIN_FILES: int = 2
DEFAULT_UPLOAD_DIR: str = str(DEFAULT_FILES_DIR)
TEMP_UPLOAD_DIR: str = "/tmp"

# ============================================================================
# FILE VALIDATION CONFIGURATION
# ============================================================================
EXPECTED_COLUMNS: int = 3
SUPPORTED_ENCODINGS: List[str] = ['utf-8-sig', 'utf-16le']

# ============================================================================
# DATA PROCESSING CONFIGURATION
# ============================================================================
DEFAULT_X_UNIT: str = 'K'
DEFAULT_Y_UNIT: str = '%'
DEFAULT_ISO_DA: float = 0.02

# ============================================================================
# UI CONFIGURATION
# ============================================================================
FILE_UPLOADER_LABEL: str = f"Choose CSV files (minimum {DEFAULT_MIN_FILES}, maximum {DEFAULT_MAX_FILES})"
APP_TITLE: str = "Picnik UI"
APP_ICON: str = ":material/analytics:"

# ============================================================================
# SESSION STATE KEYS
# ============================================================================
SESSION_KEYS: Dict[str, str] = {
    'file_paths': 'file_paths',
    'file_paths_source': 'file_paths_source',
    'file_paths_folder': 'file_paths_folder',
    'data_extractor': 'data_extractor',
    'Bnum': 'Bnum',
    'T0num': 'T0num',
    'conversion_ready': 'conversion_ready',
    'last_conversion_figure': 'last_conversion_figure',
    'extract_data_clicked': 'extract_data_clicked',
    'conversion_ranges': 'conversion_ranges',
    'plotly_plotters': 'plotly_plotters',
}

# ============================================================================
# PLOT CONFIGURATION
# ============================================================================
PLOT_X_DATA_OPTIONS: List[str] = ['temperature', 'time']
PLOT_Y_DATA_OPTIONS: List[str] = ['TG', 'DTG', 'dT/dt']
PLOT_X_UNITS: Dict[str, List[str]] = {
    'time': ['min'],
    'temperature': ['K']
}
PLOT_Y_UNITS: Dict[str, List[str]] = {
    'TG': ['%'],
    'DTG': ['%/min'],
    'dT/dt': ['K/min']
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# ENVIRONMENT-SPECIFIC SETTINGS
# ============================================================================
DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
DEVELOPMENT: bool = os.getenv("ENVIRONMENT", "development").lower() == "development"
