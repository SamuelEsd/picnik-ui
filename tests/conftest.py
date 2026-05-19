"""
Shared fixtures for picnik-ui numerical validation tests.

The pICNIK workflow is executed once per test session (scope="session") so
the expensive aVy minimization runs only once regardless of how many test
files import these fixtures.

Ground truth for the simulated dataset (Constant_E):
  - Reaction model : F1  →  f(α) = 1 − α
  - Activation energy  : E      = 75.0 kJ/mol
  - Pre-exponential    : ln(A)  = 12.0  (A in min⁻¹)
  - Heating rates      : 2.5, 5, 10, 15, 20 K/min
  - Conversion range   : T₀ = 300 K, T_f = 950 K
  - Isoconversion step : d_a = 0.005
"""

import sys
from pathlib import Path

# Ensure the tests/ directory is on sys.path so constants.py is importable
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pytest
import picnik as pnk
from constants import TRUE_BETAS, TRUE_E, TRUE_LN_A, T0_K, TF_K, ISO_T, D_ALPHA

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"

FILES = [
    str(DATA_DIR / "E_cnt_2.5.csv"),
    str(DATA_DIR / "E_cnt_5.csv"),
    str(DATA_DIR / "E_cnt_10.csv"),
    str(DATA_DIR / "E_cnt_15.csv"),
    str(DATA_DIR / "E_cnt_20.csv"),
]


# ---------------------------------------------------------------------------
# Session-scoped fixtures — computed once, shared across all tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def extraction():
    """Run DataExtraction and return (xtr, Beta, T0, isoTables)."""
    xtr = pnk.DataExtraction()
    Beta, T0 = xtr.read_files(FILES)
    xtr.Conversion(
        T0_K * np.ones(len(Beta)),
        TF_K * np.ones(len(Beta)),
    )
    isoTables = xtr.Isoconversion(d_a=D_ALPHA)
    return xtr, Beta, T0, isoTables


@pytest.fixture(scope="session")
def ace(extraction):
    """Return an ActivationEnergy object built from the shared extraction."""
    xtr, Beta, T0, isoTables = extraction
    return pnk.ActivationEnergy(Beta, T0, isoTables)


@pytest.fixture(scope="session")
def avy_result(ace):
    """Run aVy once (expensive) and cache the result for the session."""
    return ace.aVy((5, 380), var="time", p=0.90)
