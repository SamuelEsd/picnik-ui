"""
Result dataclasses for the pICNIK workflow.

Each dataclass represents the computed outputs of one workflow step and is
stored in Streamlit session state so results persist across reruns.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class IsoconversionResults:
    """Outputs of Step 6: Isoconversion Analysis."""

    temperature: pd.DataFrame
    time: pd.DataFrame
    conversion_rate: pd.DataFrame

    @property
    def raw(self) -> list:
        """List format expected by the pICNIK ActivationEnergy constructor."""
        return [self.temperature, self.time, self.conversion_rate]


@dataclass
class ActivationEnergyResults:
    """Outputs of Step 7: Activation Energy Analysis."""

    method: str
    method_label: str
    alpha: np.ndarray
    E: np.ndarray
    error: np.ndarray
    raw_result: object  # full tuple returned by pICNIK, preserved for unforeseen use


@dataclass
class CompensationEffectResults:
    """Outputs of Step 8: Compensation Effect."""

    alpha: np.ndarray
    ln_A: np.ndarray
    error_ln_A: np.ndarray
    a: float
    error_a: float
    b: float
    error_b: float
    A_fit: np.ndarray
    E_fit: np.ndarray


@dataclass
class ReconstructionResults:
    """Outputs of Step 9: Reaction Model Reconstruction."""

    g_r: np.ndarray
    alpha_plot: np.ndarray


@dataclass
class ModelfreePredictionResults:
    """Outputs of Step 10: Model-free Prediction."""

    a_prime: np.ndarray
    T_prime: np.ndarray
    t_prime: np.ndarray
    mode: str


@dataclass
class ModelbasedPredictionResults:
    """Outputs of Step 10: Model-based Isothermal Prediction."""

    t_pred: np.ndarray
    alpha_values: np.ndarray
    iso_T: float
