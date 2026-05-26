"""
Tests para el patrón Controls/Handler y validación de archivos.

Verifica que:
1. Los handlers solo computan cuando su bandera es True.
2. La bandera se apaga a False después de la ejecución (evita recomputación infinita).
3. El resultado se guarda como dataclass tipada en session state.
4. Re-correr un paso limpia los resultados de pasos posteriores.
5. FileCountValidator aplica correctamente los límites de conteo.

Nota de implementación: AppTest.from_function serializa la función app()
a un archivo temporal. Todo lo que la función necesita (imports, mocks)
debe definirse dentro de su cuerpo, sin referencias al scope exterior.
"""

from streamlit.testing.v1 import AppTest

from src.config import (
    SESS_ACTIVATION_ENERGY_RESULTS,
    SESS_DATA_EXTRACTOR,
    SESS_ISOCONVERSION_RESULT,
    SESS_PRED_MF_RESULTS,
    SESS_RUN_ISOCONVERSION,
)
from src.models.results import IsoconversionResults


# ---------------------------------------------------------------------------
# IsoconversionHandler — patrón de bandera
# ---------------------------------------------------------------------------

class TestIsoconversionHandler:

    def test_flag_resets_to_false_after_run(self):
        """SESS_RUN_ISOCONVERSION debe quedar en False después de handle_isoconversion()."""
        def app():
            import streamlit as st
            import pandas as pd
            from unittest.mock import MagicMock
            from src.components.kinetics.IsoconversionHandler import IsoconversionHandler
            from src.config import SESS_DATA_EXTRACTOR, SESS_RUN_ISOCONVERSION

            mock = MagicMock()
            df = pd.DataFrame({"0.1": [300.0], "0.5": [500.0]})
            mock.Isoconversion.return_value = (df.copy(), df.copy(), df.copy())

            st.session_state[SESS_DATA_EXTRACTOR] = mock
            st.session_state[SESS_RUN_ISOCONVERSION] = True
            IsoconversionHandler().handle_isoconversion()

        at = AppTest.from_function(app).run()
        assert at.session_state[SESS_RUN_ISOCONVERSION] is False

    def test_result_stored_as_typed_dataclass(self):
        """El resultado guardado en session state debe ser una instancia de IsoconversionResults."""
        def app():
            import streamlit as st
            import pandas as pd
            from unittest.mock import MagicMock
            from src.components.kinetics.IsoconversionHandler import IsoconversionHandler
            from src.config import SESS_DATA_EXTRACTOR, SESS_RUN_ISOCONVERSION

            mock = MagicMock()
            df = pd.DataFrame({"0.1": [300.0], "0.5": [500.0]})
            mock.Isoconversion.return_value = (df.copy(), df.copy(), df.copy())

            st.session_state[SESS_DATA_EXTRACTOR] = mock
            st.session_state[SESS_RUN_ISOCONVERSION] = True
            IsoconversionHandler().handle_isoconversion()

        at = AppTest.from_function(app).run()
        assert SESS_ISOCONVERSION_RESULT in at.session_state
        assert isinstance(at.session_state[SESS_ISOCONVERSION_RESULT], IsoconversionResults)

    def test_no_computation_when_flag_false(self):
        """Si la bandera es False, pICNIK no se llama y no se guarda ningún resultado."""
        def app():
            import streamlit as st
            import pandas as pd
            from unittest.mock import MagicMock
            from src.components.kinetics.IsoconversionHandler import IsoconversionHandler
            from src.config import SESS_DATA_EXTRACTOR, SESS_RUN_ISOCONVERSION

            mock = MagicMock()
            df = pd.DataFrame({"0.1": [300.0], "0.5": [500.0]})
            mock.Isoconversion.return_value = (df.copy(), df.copy(), df.copy())

            st.session_state[SESS_DATA_EXTRACTOR] = mock
            st.session_state[SESS_RUN_ISOCONVERSION] = False
            IsoconversionHandler().handle_isoconversion()

            st.session_state["call_count"] = mock.Isoconversion.call_count

        at = AppTest.from_function(app).run()
        assert at.session_state["call_count"] == 0
        assert SESS_ISOCONVERSION_RESULT not in at.session_state

    def test_downstream_results_cleared_on_rerun(self):
        """Re-correr isoconversión debe borrar los resultados de AE y predicciones."""
        def app():
            import streamlit as st
            import pandas as pd
            from unittest.mock import MagicMock
            from src.components.kinetics.IsoconversionHandler import IsoconversionHandler
            from src.config import (
                SESS_DATA_EXTRACTOR, SESS_RUN_ISOCONVERSION,
                SESS_ACTIVATION_ENERGY_RESULTS, SESS_PRED_MF_RESULTS,
            )

            mock = MagicMock()
            df = pd.DataFrame({"0.1": [300.0], "0.5": [500.0]})
            mock.Isoconversion.return_value = (df.copy(), df.copy(), df.copy())

            st.session_state[SESS_DATA_EXTRACTOR] = mock
            st.session_state[SESS_RUN_ISOCONVERSION] = True
            st.session_state[SESS_ACTIVATION_ENERGY_RESULTS] = "ae_obsoleto"
            st.session_state[SESS_PRED_MF_RESULTS] = "predicciones_obsoletas"
            IsoconversionHandler().handle_isoconversion()

        at = AppTest.from_function(app).run()
        assert SESS_ACTIVATION_ENERGY_RESULTS not in at.session_state
        assert SESS_PRED_MF_RESULTS not in at.session_state


# ---------------------------------------------------------------------------
# FileCountValidator
# ---------------------------------------------------------------------------

class TestFileCountValidator:

    def test_too_few_files_returns_false(self):
        """validate() devuelve False y muestra error cuando se dan menos de 2 archivos."""
        def app():
            import streamlit as st
            from src.components.file_validation.FileCountValidator import FileCountValidator
            result = FileCountValidator().validate(["solo_uno.csv"])
            st.session_state["valid"] = result

        at = AppTest.from_function(app).run()
        assert at.session_state["valid"] is False
        assert len(at.error) == 1

    def test_too_many_files_returns_false(self):
        """validate() devuelve False y muestra error cuando se dan más de 20 archivos."""
        def app():
            import streamlit as st
            from src.components.file_validation.FileCountValidator import FileCountValidator
            files = [f"archivo_{i}.csv" for i in range(21)]
            result = FileCountValidator().validate(files)
            st.session_state["valid"] = result

        at = AppTest.from_function(app).run()
        assert at.session_state["valid"] is False
        assert len(at.error) == 1

    def test_valid_count_returns_true(self):
        """validate() devuelve True para cualquier número entre 2 y 20 inclusive."""
        def app():
            import streamlit as st
            from src.components.file_validation.FileCountValidator import FileCountValidator
            files = [f"archivo_{i}.csv" for i in range(5)]
            result = FileCountValidator().validate(files)
            st.session_state["valid"] = result

        at = AppTest.from_function(app).run()
        assert at.session_state["valid"] is True
