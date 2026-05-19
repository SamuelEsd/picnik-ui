"""
Pruebas de validación — Paso 3: Predicciones (modelfree_prediction)

El proceso simulado sigue el modelo F1: f(α) = 1 − α, con E = 75 kJ/mol y
ln(A/min) = 12. Bajo condiciones isotérmicas a temperatura T₀, la solución
analítica exacta es:

    α(t) = 1 − exp(−A · exp(−E / RT₀) · t)

Se verifica que la predicción isoconversional de pICNIK concuerda con esta
solución analítica con un error absoluto máximo < 0.01 en α ∈ [0.05, 0.95].
"""

import numpy as np
import pytest
from constants import TRUE_E, TRUE_LN_A, ISO_T

R_kJ = 0.0083144626  # constante de los gases en kJ mol⁻¹ K⁻¹


def alpha_f1_isotermica(t, E_kJ, lnA, T_K):
    """Solución analítica para el modelo F1 bajo temperatura isotérmica."""
    A = np.exp(lnA)
    return 1.0 - np.exp(-A * np.exp(-E_kJ / (R_kJ * T_K)) * t)


class TestPrediccionIsotermica:

    @pytest.fixture(scope="class")
    def pred_iso(self, ace, avy_result):
        """Ejecuta la predicción isotérmica a T = 575 K y devuelve (alpha, T, t)."""
        Ea = avy_result[2]
        ap, Tp, tp = ace.modelfree_prediction(
            Ea, B=0, isoT=ISO_T, alpha=0.999, bounds=(10, 10)
        )
        return ap, Tp, tp

    def test_prediction_completa_rango_alpha(self, pred_iso):
        """La predicción cubre el rango α ∈ [0, 0.999]."""
        ap, _, _ = pred_iso
        assert ap.min() >= 0.0
        assert ap.max() >= 0.95, f"La predicción solo llega hasta α = {ap.max():.3f}"

    def test_temperatura_constante(self, pred_iso):
        """En modo isotérmico, T se mantiene constante en ISO_T (575 K)."""
        _, Tp, _ = pred_iso
        np.testing.assert_allclose(
            Tp, ISO_T * np.ones_like(Tp), atol=1.0,
            err_msg="La temperatura predicha no es constante en modo isotérmico",
        )

    def test_error_maximo_vs_solucion_analitica(self, pred_iso):
        """Error absoluto máximo vs solución analítica F1 < 0.01 (en α ∈ [0.05, 0.95])."""
        ap, _, tp = pred_iso

        alpha_ref = alpha_f1_isotermica(tp, TRUE_E, TRUE_LN_A, ISO_T)

        # Restringir comparación a la zona central, donde ambas soluciones
        # están bien definidas (evitar los extremos ruidosos).
        mask = (ap >= 0.05) & (ap <= 0.95)
        error_max = np.abs(ap[mask] - alpha_ref[mask]).max()

        assert error_max < 0.01, (
            f"Error máximo vs solución analítica F1: {error_max:.4f} "
            f"(límite aceptable: 0.01)"
        )

    def test_tiempo_monotono_creciente(self, pred_iso):
        """El tiempo de predicción es monótonamente creciente."""
        _, _, tp = pred_iso
        diffs = np.diff(tp)
        assert np.all(diffs >= 0), "El vector de tiempo de predicción no es monótono"


class TestPrediccionNoIsotermica:

    @pytest.fixture(scope="class")
    def pred_noniso(self, ace, avy_result, extraction):
        """Predicción no isotérmica a β = 10 K/min."""
        xtr, _, _, _ = extraction
        Ea = avy_result[2]
        ap, Tp, tp = ace.modelfree_prediction(
            Ea, B=10, alpha=0.999, bounds=(10, 10)
        )
        return ap, Tp, tp, xtr

    def test_conversion_monotona(self, pred_noniso):
        """α(t) es monótonamente creciente en la predicción no isotérmica."""
        ap, _, _, _ = pred_noniso
        assert np.all(np.diff(ap) >= -1e-6), "α(t) no es monótono en la predicción no isotérmica"

    def test_temperatura_monotona(self, pred_noniso):
        """T(t) es monótonamente creciente (rampa lineal)."""
        _, Tp, _, _ = pred_noniso
        assert np.all(np.diff(Tp) >= -1e-6), "T(t) no es monótona en la predicción no isotérmica"

    def test_prediccion_cubre_datos_experimentales(self, pred_noniso):
        """El rango de T predicho solapa con el rango del experimento a β = 10 K/min."""
        _, Tp, _, xtr = pred_noniso
        # Experimento a β = 10 K/min es el índice 2 (0-indexed: 2.5, 5, 10, ...)
        T_exp = xtr.T[2]
        assert Tp.min() <= T_exp.mean() <= Tp.max(), (
            "El rango de temperatura de la predicción no incluye el rango experimental"
        )
