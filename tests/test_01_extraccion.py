"""
Pruebas de validación — Paso 1: Extracción de datos (DataExtraction)

Verifica que DataExtraction lee correctamente los archivos CSV del proceso
simulado y calcula los parámetros de entrada que todos los métodos de
isoconversión requieren.
"""

import numpy as np
import pytest
from constants import TRUE_BETAS, T0_K, TF_K


class TestExtraccion:

    def test_numero_de_experimentos(self, extraction):
        """Se leen exactamente los 5 archivos proporcionados."""
        xtr, Beta, T0, _ = extraction
        assert len(Beta) == 5

    def test_velocidades_de_calentamiento(self, extraction):
        """Las β computadas por regresión lineal coinciden con las reales (< 1 % de error)."""
        _, Beta, _, _ = extraction
        np.testing.assert_allclose(
            np.sort(Beta),
            TRUE_BETAS,
            rtol=0.01,
            err_msg="Las velocidades de calentamiento calculadas difieren de las programadas en >1 %",
        )

    def test_temperatura_inicial(self, extraction):
        """La temperatura inicial de cada experimento es ≈ 300 K (= T₀ del proceso simulado)."""
        _, _, T0, _ = extraction
        np.testing.assert_allclose(
            T0,
            T0_K * np.ones_like(T0),
            atol=5.0,  # ±5 K — margen para el instante de inicio del registro
            err_msg="La temperatura inicial difiere de 300 K en más de 5 K",
        )

    def test_rango_de_conversion(self, extraction):
        """α ∈ [0, 1] para todos los experimentos tras aplicar Conversion()."""
        xtr, _, _, _ = extraction
        for i, alpha_i in enumerate(xtr.alpha):
            assert alpha_i.min() >= -1e-6, f"α negativo en experimento {i}"
            assert alpha_i.max() <= 1 + 1e-6, f"α > 1 en experimento {i}"

    def test_tablas_isoconversionales_no_vacias(self, extraction):
        """Isoconversion() retorna tablas con al menos un punto de α."""
        _, _, _, isoTables = extraction
        # isoTables es una tupla; el primer elemento es la tabla de temperatura
        TempIsoDF = isoTables[0]
        assert len(TempIsoDF) > 0, "La tabla de isoconversión de temperatura está vacía"

    def test_tablas_isoconversionales_sin_nan(self, extraction):
        """Las tablas de isoconversión no contienen NaN."""
        _, _, _, isoTables = extraction
        for tabla in isoTables:
            assert not np.any(np.isnan(tabla.values)), \
                "Se encontraron NaN en las tablas de isoconversión"
