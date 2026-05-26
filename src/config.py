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
# SESSION STATE KEY CONSTANTS
# ============================================================================

# UI / locale
SESS_LOCALE: str = 'locale'

# Core data objects
SESS_FILE_PATHS: str = 'file_paths'
SESS_FILE_SOURCE: str = 'file_paths_source'
SESS_FILE_FOLDER: str = 'file_paths_folder'
SESS_BNUM: str = 'Bnum'
SESS_T0_NUM: str = 'T0num'
SESS_DATA_EXTRACTOR: str = 'data_extractor'
SESS_CONVERSION_RANGES: str = 'conversion_ranges'
SESS_ACTIVATION_ENERGY_OBJECT: str = 'activation_energy_object'

# Extraction
SESS_CONVERSION_READY: str = 'conversion_ready'
SESS_EXTRACT_CLICKED: str = 'extract_data_clicked'
SESS_PLOTLY_PLOTTERS: str = 'plotly_plotters'

# Conversion (Step 5)
SESS_RUN_CONVERSION: str = 'run_conversion_clicked'
SESS_CONVERSION_METADATA: str = 'conversion_metadata'
SESS_CONVERSION_PLOTTER: str = 'conversion_plotter'

# Isoconversion (Step 6)
SESS_RUN_ISOCONVERSION: str = 'run_isoconversion_clicked'
SESS_ISO_DA: str = 'isoconversion_d_a'

# Activation Energy (Step 7)
SESS_RUN_AE: str = 'run_ae_clicked'
SESS_AE_METHOD: str = 'selected_ae_method'        # legacy single-method key (kept for compat)
SESS_AE_METHODS: str = 'selected_ae_methods'       # list[str] of checked methods
SESS_AE_ACTIVE_METHOD: str = 'ae_active_method'    # which method's E to feed downstream steps
SESS_AE_SHOW_ERROR: str = 'ae_show_error_bars'     # bool toggle for error bars in chart
SESS_AVY_P_VALUE: str = 'avy_p_value'
SESS_VY_BOUNDS: str = 'vy_bounds'

# Compensation Effect (Step 8)
SESS_RUN_COMP: str = 'run_comp_clicked'
SESS_COMP_COL: str = 'comp_col'
SESS_COMP_ERROR_M: str = 'comp_error_m'

# Reconstruction (Step 9)
SESS_RUN_RECON: str = 'run_recon_clicked'
SESS_RECON_BETA_IDX: str = 'recon_beta_idx'

# Predictions (Step 10)
SESS_RUN_PRED_MF: str = 'run_pred_mf_clicked'
SESS_RUN_PRED_MB: str = 'run_pred_mb_clicked'
SESS_PRED_MODE: str = 'pred_mode'
SESS_PRED_ALPHA_TARGET: str = 'pred_alpha_target'
SESS_PRED_BOUNDS: str = 'pred_bounds'
SESS_PRED_ISO_T: str = 'pred_iso_T'
SESS_PRED_LINEAR_B: str = 'pred_linear_B'
SESS_PRED_MB_ISO_T: str = 'pred_mb_iso_T'
SESS_PRED_MB_COL: str = 'pred_mb_col'

# Result objects (one per workflow step — store typed dataclasses from src.models.results)
SESS_ISOCONVERSION_RESULT: str = 'isoconversion_result'
SESS_ACTIVATION_ENERGY_RESULTS: str = 'activation_energy_results'
SESS_COMP_RESULTS: str = 'comp_results'
SESS_RECON_RESULTS: str = 'recon_results'
SESS_PRED_MF_RESULTS: str = 'pred_mf_results'
SESS_PRED_MB_RESULTS: str = 'pred_mb_results'

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
