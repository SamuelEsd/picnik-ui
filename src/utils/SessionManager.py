"""
Session state management utilities.
"""

import streamlit as st
from typing import List, Optional

from src.config import (
    SESS_FILE_PATHS,
    SESS_FILE_SOURCE,
    SESS_FILE_FOLDER,
    SESS_BNUM,
    SESS_T0_NUM,
    SESS_DATA_EXTRACTOR,
    SESS_CONVERSION_RANGES,
    SESS_CONVERSION_READY,
    SESS_EXTRACT_CLICKED,
    SESS_PLOTLY_PLOTTERS,
    SESS_CONVERSION_PLOTTER,
    SESS_CONVERSION_METADATA,
    SESS_ISOCONVERSION_RESULT,
    SESS_ACTIVATION_ENERGY_OBJECT,
    SESS_ACTIVATION_ENERGY_RESULTS,
    SESS_AE_ACTIVE_METHOD,
    SESS_COMP_RESULTS,
    SESS_RECON_RESULTS,
    SESS_PRED_MF_RESULTS,
    SESS_PRED_MB_RESULTS,
)
from src.models.results import ActivationEnergyResults

# Pipeline dependency map.
# _STEP_ORDER defines the execution order of the wizard steps.
# _STEP_RESULT_KEYS maps each step to the session keys it produces.
# clear_downstream_from(step) uses these to invalidate every step that follows.
_STEP_ORDER: List[str] = [
    "extraction",
    "conversion",
    "isoconversion",
    "activation_energy",
    "compensation",
    "reconstruction",
    "predictions",
]

_STEP_RESULT_KEYS: dict = {
    "extraction":        [SESS_DATA_EXTRACTOR, SESS_BNUM, SESS_T0_NUM,
                          SESS_CONVERSION_READY, SESS_EXTRACT_CLICKED, SESS_PLOTLY_PLOTTERS],
    "conversion":        [SESS_CONVERSION_METADATA, SESS_CONVERSION_PLOTTER],
    "isoconversion":     [SESS_ISOCONVERSION_RESULT],
    "activation_energy": [SESS_ACTIVATION_ENERGY_OBJECT, SESS_ACTIVATION_ENERGY_RESULTS],
    "compensation":      [SESS_COMP_RESULTS],
    "reconstruction":    [SESS_RECON_RESULTS],
    "predictions":       [SESS_PRED_MF_RESULTS, SESS_PRED_MB_RESULTS],
}


class SessionManager:
    """Centralized management of Streamlit session state."""

    @staticmethod
    def delete_multiple(keys: list) -> None:
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]

    @staticmethod
    def clear_downstream_from(step: str) -> None:
        """Delete session results for every pipeline step that comes after `step`.

        Call this inside a handler's computation block to ensure that stale
        results from later steps are removed before new results are stored.
        When adding a new wizard step, add its result keys to _STEP_RESULT_KEYS
        and its name to _STEP_ORDER — clear_downstream_from will handle it automatically.
        """
        if step not in _STEP_ORDER:
            raise ValueError(f"Unknown step '{step}'. Valid steps: {_STEP_ORDER}")
        idx = _STEP_ORDER.index(step)
        for downstream in _STEP_ORDER[idx + 1:]:
            SessionManager.delete_multiple(_STEP_RESULT_KEYS[downstream])

    @staticmethod
    def clear_extraction_state() -> None:
        """Full pipeline reset when new files are loaded.

        Clears user-input state (file paths, conversion ranges) and all
        computed results across every pipeline step.
        """
        SessionManager.delete_multiple([SESS_FILE_PATHS, SESS_CONVERSION_RANGES])
        for step in _STEP_ORDER:
            SessionManager.delete_multiple(_STEP_RESULT_KEYS[step])

    @staticmethod
    def is_conversion_ready() -> bool:
        return st.session_state.get(SESS_CONVERSION_READY, False)

    @staticmethod
    def get_file_paths() -> list:
        return st.session_state.get(SESS_FILE_PATHS, [])

    @staticmethod
    def set_file_paths(paths: list, source: str = 'default', folder: str = '') -> None:
        st.session_state[SESS_FILE_PATHS] = paths
        st.session_state[SESS_FILE_SOURCE] = source
        if folder:
            st.session_state[SESS_FILE_FOLDER] = folder

    @staticmethod
    def get_active_ae_result() -> Optional[ActivationEnergyResults]:
        """Return the ActivationEnergyResults chosen as source for downstream steps.

        Reads SESS_AE_ACTIVE_METHOD to pick the user-selected method.
        Falls back to the most rigorous available method: aVy > Vy > KAS > OFW > Fr.
        """
        results = st.session_state.get(SESS_ACTIVATION_ENERGY_RESULTS)
        if results is None:
            return None
        if isinstance(results, dict):
            active = st.session_state.get(SESS_AE_ACTIVE_METHOD)
            if active and active in results:
                return results[active]
            for method in ("aVy", "Vy", "KAS", "OFW", "Fr"):
                if method in results:
                    return results[method]
            return None
        return results  # legacy: single ActivationEnergyResults
