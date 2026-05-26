"""
Tests para SessionManager — flujo del estado de sesión.

Verifica que clear_downstream_from(), clear_extraction_state() y
get_active_ae_result() se comportan correctamente: son el mecanismo que
impide que datos obsoletos se propaguen por el pipeline del wizard.

Nota de implementación: AppTest.from_function serializa la función app()
a un archivo temporal vía inspect.getsource(). Las variables del scope
exterior no están disponibles adentro; cada app() debe importar todo lo
que necesite.
"""

import pytest
from streamlit.testing.v1 import AppTest

from src.config import (
    SESS_AE_ACTIVE_METHOD,
    SESS_ACTIVATION_ENERGY_RESULTS,
    SESS_COMP_RESULTS,
    SESS_CONVERSION_METADATA,
    SESS_CONVERSION_RANGES,
    SESS_DATA_EXTRACTOR,
    SESS_FILE_PATHS,
    SESS_ISOCONVERSION_RESULT,
    SESS_PRED_MB_RESULTS,
    SESS_PRED_MF_RESULTS,
    SESS_RECON_RESULTS,
)


# ---------------------------------------------------------------------------
# clear_downstream_from
# ---------------------------------------------------------------------------

class TestClearDownstreamFrom:

    def test_isoconversion_clears_ae_and_below(self):
        """El paso de isoconversión no se borra a sí mismo, pero sí todo lo que le sigue."""
        def app():
            import streamlit as st
            from src.utils.SessionManager import SessionManager
            from src.config import (
                SESS_ISOCONVERSION_RESULT, SESS_ACTIVATION_ENERGY_RESULTS,
                SESS_COMP_RESULTS, SESS_RECON_RESULTS,
                SESS_PRED_MF_RESULTS, SESS_PRED_MB_RESULTS,
            )
            st.session_state[SESS_ISOCONVERSION_RESULT] = "iso"
            st.session_state[SESS_ACTIVATION_ENERGY_RESULTS] = "ae"
            st.session_state[SESS_COMP_RESULTS] = "comp"
            st.session_state[SESS_RECON_RESULTS] = "recon"
            st.session_state[SESS_PRED_MF_RESULTS] = "pred_mf"
            st.session_state[SESS_PRED_MB_RESULTS] = "pred_mb"
            st.session_state["_ok"] = True
            SessionManager.clear_downstream_from("isoconversion")

        at = AppTest.from_function(app).run()

        assert "_ok" in at.session_state, "La función app() no llegó a ejecutarse"
        assert at.session_state[SESS_ISOCONVERSION_RESULT] == "iso"   # no se toca
        assert SESS_ACTIVATION_ENERGY_RESULTS not in at.session_state
        assert SESS_COMP_RESULTS not in at.session_state
        assert SESS_RECON_RESULTS not in at.session_state
        assert SESS_PRED_MF_RESULTS not in at.session_state
        assert SESS_PRED_MB_RESULTS not in at.session_state

    def test_conversion_clears_iso_and_below(self):
        """clear_downstream_from('conversion') borra isoconversión y todo lo que sigue."""
        def app():
            import streamlit as st
            from src.utils.SessionManager import SessionManager
            from src.config import (
                SESS_CONVERSION_METADATA, SESS_ISOCONVERSION_RESULT,
                SESS_ACTIVATION_ENERGY_RESULTS, SESS_PRED_MF_RESULTS,
            )
            st.session_state[SESS_CONVERSION_METADATA] = "meta"
            st.session_state[SESS_ISOCONVERSION_RESULT] = "iso"
            st.session_state[SESS_ACTIVATION_ENERGY_RESULTS] = "ae"
            st.session_state[SESS_PRED_MF_RESULTS] = "pred"
            st.session_state["_ok"] = True
            SessionManager.clear_downstream_from("conversion")

        at = AppTest.from_function(app).run()

        assert "_ok" in at.session_state, "La función app() no llegó a ejecutarse"
        assert at.session_state[SESS_CONVERSION_METADATA] == "meta"   # no se toca
        assert SESS_ISOCONVERSION_RESULT not in at.session_state
        assert SESS_ACTIVATION_ENERGY_RESULTS not in at.session_state
        assert SESS_PRED_MF_RESULTS not in at.session_state

    def test_unknown_step_raises_value_error(self):
        """Un nombre de paso desconocido levanta ValueError, no falla silenciosamente."""
        def app():
            import streamlit as st
            from src.utils.SessionManager import SessionManager
            try:
                SessionManager.clear_downstream_from("paso_inexistente")
                st.session_state["raised"] = False
            except ValueError:
                st.session_state["raised"] = True

        at = AppTest.from_function(app).run()
        assert at.session_state["raised"] is True


# ---------------------------------------------------------------------------
# clear_extraction_state
# ---------------------------------------------------------------------------

class TestClearExtractionState:

    def test_removes_file_paths_and_all_pipeline_results(self):
        """Cargar archivos nuevos debe borrar rutas, rangos y todos los resultados previos."""
        def app():
            import streamlit as st
            from src.utils.SessionManager import SessionManager
            from src.config import (
                SESS_FILE_PATHS, SESS_CONVERSION_RANGES, SESS_DATA_EXTRACTOR,
                SESS_ISOCONVERSION_RESULT, SESS_ACTIVATION_ENERGY_RESULTS,
                SESS_PRED_MF_RESULTS,
            )
            st.session_state[SESS_FILE_PATHS] = ["/datos/exp.csv"]
            st.session_state[SESS_CONVERSION_RANGES] = {0: (300, 900)}
            st.session_state[SESS_DATA_EXTRACTOR] = "xtr"
            st.session_state[SESS_ISOCONVERSION_RESULT] = "iso"
            st.session_state[SESS_ACTIVATION_ENERGY_RESULTS] = "ae"
            st.session_state[SESS_PRED_MF_RESULTS] = "pred"
            st.session_state["_ok"] = True
            SessionManager.clear_extraction_state()

        at = AppTest.from_function(app).run()

        assert "_ok" in at.session_state, "La función app() no llegó a ejecutarse"
        assert SESS_FILE_PATHS not in at.session_state
        assert SESS_CONVERSION_RANGES not in at.session_state
        assert SESS_DATA_EXTRACTOR not in at.session_state
        assert SESS_ISOCONVERSION_RESULT not in at.session_state
        assert SESS_ACTIVATION_ENERGY_RESULTS not in at.session_state
        assert SESS_PRED_MF_RESULTS not in at.session_state


# ---------------------------------------------------------------------------
# get_active_ae_result
# ---------------------------------------------------------------------------

class TestGetActiveAeResult:

    def test_returns_none_when_no_results_in_session(self):
        """Devuelve None si SESS_ACTIVATION_ENERGY_RESULTS no existe."""
        def app():
            import streamlit as st
            from src.utils.SessionManager import SessionManager
            result = SessionManager.get_active_ae_result()
            st.session_state["is_none"] = result is None

        at = AppTest.from_function(app).run()
        assert at.session_state["is_none"] is True

    def test_returns_user_selected_method(self):
        """Cuando el usuario eligió un método activo, devuelve ese y no otro."""
        def app():
            import streamlit as st
            import numpy as np
            from src.utils.SessionManager import SessionManager
            from src.config import SESS_ACTIVATION_ENERGY_RESULTS, SESS_AE_ACTIVE_METHOD
            from src.models.results import ActivationEnergyResults

            alpha = np.linspace(0.1, 0.9, 9)
            kas = ActivationEnergyResults(
                method="KAS", method_label="KAS",
                alpha=alpha, E=75.0 * np.ones_like(alpha),
                error=0.5 * np.ones_like(alpha), raw_result=None,
            )
            vy = ActivationEnergyResults(
                method="Vy", method_label="Vy",
                alpha=alpha, E=74.0 * np.ones_like(alpha),
                error=0.4 * np.ones_like(alpha), raw_result=None,
            )
            st.session_state[SESS_ACTIVATION_ENERGY_RESULTS] = {"KAS": kas, "Vy": vy}
            st.session_state[SESS_AE_ACTIVE_METHOD] = "KAS"
            result = SessionManager.get_active_ae_result()
            st.session_state["method"] = result.method if result else None

        at = AppTest.from_function(app).run()
        assert at.session_state["method"] == "KAS"

    def test_fallback_prefers_avy_over_kas(self):
        """Sin método activo seleccionado, el fallback prefiere aVy sobre KAS."""
        def app():
            import streamlit as st
            import numpy as np
            from src.utils.SessionManager import SessionManager
            from src.config import SESS_ACTIVATION_ENERGY_RESULTS
            from src.models.results import ActivationEnergyResults

            alpha = np.linspace(0.1, 0.9, 9)
            avy = ActivationEnergyResults(
                method="aVy", method_label="aVy",
                alpha=alpha, E=75.0 * np.ones_like(alpha),
                error=0.5 * np.ones_like(alpha), raw_result=None,
            )
            kas = ActivationEnergyResults(
                method="KAS", method_label="KAS",
                alpha=alpha, E=75.0 * np.ones_like(alpha),
                error=0.5 * np.ones_like(alpha), raw_result=None,
            )
            st.session_state[SESS_ACTIVATION_ENERGY_RESULTS] = {"KAS": kas, "aVy": avy}
            # sin SESS_AE_ACTIVE_METHOD — debe aplicar el orden de fallback
            result = SessionManager.get_active_ae_result()
            st.session_state["method"] = result.method if result else None

        at = AppTest.from_function(app).run()
        assert at.session_state["method"] == "aVy"
