"""
Internationalization (i18n) support using GNU gettext.

Usage:
    from src.i18n import _
    st.title(_("Welcome"))

Language is stored in st.session_state["locale"] and can be changed at runtime.
Translatable strings are extracted with: pybabel extract -F babel.cfg -o locales/messages.pot .
"""

import gettext
from functools import lru_cache
from pathlib import Path

import streamlit as st

from src.config import SESS_LOCALE

LOCALES_DIR = Path(__file__).parent.parent / "locales"
SUPPORTED_LOCALES: dict[str, str] = {
    "en": "English",
    "es": "Español",
}
DEFAULT_LOCALE = "en"


def get_locale() -> str:
    return st.session_state.get(SESS_LOCALE, DEFAULT_LOCALE)


@lru_cache(maxsize=None)
def _load_translator(locale: str) -> gettext.GNUTranslations | gettext.NullTranslations:
    try:
        return gettext.translation("messages", localedir=str(LOCALES_DIR), languages=[locale])
    except FileNotFoundError:
        return gettext.NullTranslations()


def _(text: str) -> str:
    """Return the translation of text for the current locale."""
    return _load_translator(get_locale()).gettext(text)


def language_selector() -> None:
    """Render a language selector widget in the sidebar."""
    options = list(SUPPORTED_LOCALES.keys())
    labels = list(SUPPORTED_LOCALES.values())
    current = get_locale()

    selected_label = st.selectbox(
        label="Language / Idioma",
        options=labels,
        index=options.index(current) if current in options else 0,
    )

    selected_locale = options[labels.index(selected_label)]
    if selected_locale != current:
        st.session_state[SESS_LOCALE] = selected_locale
        st.rerun()
