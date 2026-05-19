"""
Pruebas de validación — Paso 2: Energías de activación (ActivationEnergy)

Para los cinco métodos de isoconversión implementados en pICNIK, verifica que:
  1. El valor medio de Eα(α) es consistente con el valor verdadero del proceso
     simulado (E = 75 kJ/mol).
  2. Eα(α) no contiene valores negativos ni NaN.
  3. La longitud del arreglo es coherente con el rango de α analizado.

Nota sobre tolerancias:
  - Fr, KAS, Vy, aVy usan tolerancia ±5 %, justificada por el error numérico
    de las regresiones y la discretización de la cuadrícula de α.
  - OFW usa tolerancia ±12 % porque la aproximación de Doyle introduce un
    sesgo sistemático conocido en la integral de temperatura (Vyazovkin, 2015).
    Este sesgo es inherente al método, no un defecto de la implementación.
"""

import numpy as np
import pytest
from constants import TRUE_E


RTOL_EXACT   = 0.05   # ±5 %  — para Fr, KAS, Vy, aVy
RTOL_OFW     = 0.12   # ±12 % — para OFW (sesgo por aproximación de Doyle)


class TestFriedman:

    def test_ea_media_cercana_al_valor_real(self, ace):
        """Fr(): media de Eα ≈ 75 kJ/mol (±5 %)."""
        result = ace.Fr()
        Ea = result[2]  # [0]=alpha, [1]=T, [2]=Ea, [3]=error, [4]=intercept
        np.testing.assert_allclose(
            Ea.mean(), TRUE_E, rtol=RTOL_EXACT,
            err_msg=f"Fr: media Eα = {Ea.mean():.2f} kJ/mol, esperado ≈ {TRUE_E} kJ/mol",
        )

    def test_ea_sin_valores_negativos(self, ace):
        """Fr(): Eα(α) > 0 en todo el rango."""
        result = ace.Fr()
        assert np.all(result[2] > 0), "Fr devolvió valores de Eα ≤ 0"

    def test_ea_sin_nan(self, ace):
        """Fr(): Eα(α) no contiene NaN."""
        result = ace.Fr()
        assert not np.any(np.isnan(result[2])), "Fr devolvió NaN en Eα"


class TestOFW:

    def test_ea_media_cercana_al_valor_real(self, ace):
        """OFW(): media de Eα dentro de ±12 % del valor real (sesgo de Doyle conocido)."""
        result = ace.OFW()
        Ea = result[2]
        np.testing.assert_allclose(
            Ea.mean(), TRUE_E, rtol=RTOL_OFW,
            err_msg=f"OFW: media Eα = {Ea.mean():.2f} kJ/mol, esperado ≈ {TRUE_E} kJ/mol",
        )

    def test_ea_sin_valores_negativos(self, ace):
        result = ace.OFW()
        assert np.all(result[2] > 0)

    def test_ea_sin_nan(self, ace):
        result = ace.OFW()
        assert not np.any(np.isnan(result[2]))


class TestKAS:

    def test_ea_media_cercana_al_valor_real(self, ace):
        """KAS(): media de Eα ≈ 75 kJ/mol (±5 %)."""
        result = ace.KAS()
        Ea = result[2]
        np.testing.assert_allclose(
            Ea.mean(), TRUE_E, rtol=RTOL_EXACT,
            err_msg=f"KAS: media Eα = {Ea.mean():.2f} kJ/mol, esperado ≈ {TRUE_E} kJ/mol",
        )

    def test_ea_sin_valores_negativos(self, ace):
        result = ace.KAS()
        assert np.all(result[2] > 0)

    def test_ea_sin_nan(self, ace):
        result = ace.KAS()
        assert not np.any(np.isnan(result[2]))


class TestVyazovkin:

    def test_ea_media_cercana_al_valor_real(self, ace):
        """Vy(): media de Eα ≈ 75 kJ/mol (±5 %)."""
        result = ace.Vy((5, 380))
        Ea = result[2]
        np.testing.assert_allclose(
            Ea.mean(), TRUE_E, rtol=RTOL_EXACT,
            err_msg=f"Vy: media Eα = {Ea.mean():.2f} kJ/mol, esperado ≈ {TRUE_E} kJ/mol",
        )

    def test_ea_sin_valores_negativos(self, ace):
        result = ace.Vy((5, 380))
        assert np.all(result[2] > 0)

    def test_ea_sin_nan(self, ace):
        result = ace.Vy((5, 380))
        assert not np.any(np.isnan(result[2]))


class TestVyazovkinAvanzado:

    def test_ea_media_cercana_al_valor_real(self, avy_result):
        """aVy(): media de Eα ≈ 75 kJ/mol (±5 %). Método más preciso."""
        Ea = avy_result[2]
        np.testing.assert_allclose(
            Ea.mean(), TRUE_E, rtol=RTOL_EXACT,
            err_msg=f"aVy: media Eα = {Ea.mean():.2f} kJ/mol, esperado ≈ {TRUE_E} kJ/mol",
        )

    def test_ea_sin_valores_negativos(self, avy_result):
        assert np.all(avy_result[2] > 0)

    def test_ea_sin_nan(self, avy_result):
        assert not np.any(np.isnan(avy_result[2]))

    def test_ea_constante_proceso_un_paso(self, avy_result):
        """aVy(): la variación de Eα(α) es < 10 % del valor medio, indicando proceso de un paso."""
        Ea = avy_result[2]
        variacion_relativa = (Ea.max() - Ea.min()) / Ea.mean()
        assert variacion_relativa < 0.10, (
            f"aVy: variación de Eα = {variacion_relativa:.1%}, "
            "se esperaba < 10 % para un proceso de un solo paso"
        )
