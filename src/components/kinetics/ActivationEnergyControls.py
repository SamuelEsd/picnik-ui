"""
Activation Energy Controls Component

Renders the UI controls for activation energy method selection.
"""

import streamlit as st

from src.utils.SessionManager import SessionManager
from src.config import (
    SESS_ISOCONVERSION_RESULT,
    SESS_RUN_AE,
    SESS_AE_METHODS,
    SESS_AE_SHOW_ERROR,
    SESS_AVY_P_VALUE,
    SESS_VY_BOUNDS,
)

AE_METHODS = {
    "Fr":  "Friedman method",
    "KAS": "Kissinger-Akahira-Sunose method",
    "OFW": "Ozawa-Flynn-Wall method",
    "Vy":  "Vyazovkin method",
    "aVy": "Advanced Vyazovkin method",
}

# Color assigned to each method — used in checkboxes and in the combined plot.
AE_METHOD_COLORS = {
    "Fr":  "#1f77b4",  # blue
    "OFW": "#ff7f0e",  # orange
    "KAS": "#2ca02c",  # green
    "Vy":  "#9467bd",  # purple
    "aVy": "#d62728",  # red
}


class ActivationEnergyControls:
    """Renders the UI controls for activation energy method selection."""

    def render(self) -> None:
        """Display activation energy method selection controls."""
        st.divider()
        st.subheader("Step 7: Activation Energy Analysis")

        if SessionManager.get(SESS_ISOCONVERSION_RESULT) is None:
            st.info("Complete Step 6 (Isoconversion) first to enable activation energy analysis.")
            return

        st.write("**Select one or more methods to compute activation energy:**")

        col_methods, col_action = st.columns([3, 1])

        with col_methods:
            selected_methods = []
            for key, label in AE_METHODS.items():
                color = AE_METHOD_COLORS[key]
                dot_col, check_col = st.columns([0.04, 0.96])
                with dot_col:
                    st.markdown(
                        f'<div style="width:14px;height:14px;border-radius:3px;'
                        f'background:{color};margin-top:8px"></div>',
                        unsafe_allow_html=True,
                    )
                with check_col:
                    previously_checked = key in SessionManager.get(SESS_AE_METHODS, [])
                    checked = st.checkbox(label, value=previously_checked, key=f"ae_method_{key}")
                if checked:
                    selected_methods.append(key)

            SessionManager.set(SESS_AE_METHODS, selected_methods)

            # Vy / aVy shared bounds — show when either is selected
            if "Vy" in selected_methods or "aVy" in selected_methods:
                saved_bounds = SessionManager.get(SESS_VY_BOUNDS, (1.0, 300.0))
                st.write("**Search bounds for E (kJ/mol) — Vy / aVy:**")
                bounds_col1, bounds_col2 = st.columns(2)
                with bounds_col1:
                    bound_low = st.number_input(
                        "Lower bound",
                        min_value=0.1,
                        value=float(saved_bounds[0]),
                        step=1.0,
                        help="Minimum E value (kJ/mol) the minimizer will consider.",
                        key="vy_bound_low",
                    )
                with bounds_col2:
                    bound_high = st.number_input(
                        "Upper bound",
                        min_value=0.1,
                        value=float(saved_bounds[1]),
                        step=1.0,
                        help="Maximum E value (kJ/mol). The true E must fall within [lower, upper].",
                        key="vy_bound_high",
                    )
                if bound_low >= bound_high:
                    st.warning("Lower bound must be less than upper bound.")
                else:
                    SessionManager.set(SESS_VY_BOUNDS, (bound_low, bound_high))

            # aVy-only p-value slider
            if "aVy" in selected_methods:
                p_value = st.slider(
                    "Confidence level (Advanced Vyazovkin)",
                    min_value=0.50,
                    max_value=0.99,
                    step=0.01,
                    value=SessionManager.get(SESS_AVY_P_VALUE, 0.90),
                    help="Confidence level for the error estimation of the Vyazovkin advanced method.",
                    key="avy_p_slider",
                )
                SessionManager.set(SESS_AVY_P_VALUE, p_value)

            # Error bar toggle
            st.write("")
            show_error = st.toggle(
                "Show error bars",
                value=SessionManager.get(SESS_AE_SHOW_ERROR, True),
                help="Display 95% confidence interval error bars on the E(α) chart.",
                key="ae_show_error_toggle",
            )
            SessionManager.set(SESS_AE_SHOW_ERROR, show_error)

        with col_action:
            st.write("")
            st.write("")
            if st.button(
                "Calculate Activation Energy",
                type="primary",
                key="ae_calculate_btn",
            ):
                if not selected_methods:
                    st.warning("Select at least one method before calculating.")
                else:
                    SessionManager.set(SESS_RUN_AE, True)
