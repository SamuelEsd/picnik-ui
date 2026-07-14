"""
Walkthrough Tutorial View — static screenshot-based guide.
"""

import streamlit as st

from src.config import APP_TITLE, RESOURCES_DIR
from src.i18n import _

SCREENSHOTS = RESOURCES_DIR / "Screenshots"


def _img(name: str, caption: str) -> None:
    """Display a walkthrough screenshot."""
    path = SCREENSHOTS / name
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.warning(f"Screenshot not found: {name}")


def main():
    st.title(f"{APP_TITLE} — {_('Tutorial')}")
    st.markdown(_(
        "This tutorial walks you through the **Tool** page step by step. "
        "Follow the instructions in each section, then open the **Tool** page from the sidebar to run your own analysis."
    ))

    # ------------------------------------------------------------------ #
    # STEP 1 — Data Source Selection                                       #
    # ------------------------------------------------------------------ #
    st.header(_("Step 1 — Data Source Selection"))
    st.info(_(
        "At the top of the Tool page, choose how to load your data:\n\n"
        "- **Select default dataset** — pick one of the built-in datasets from the dropdown "
        "(e.g. `constant_E`). The tool loads all CSV files in that folder automatically.\n"
        "- **Upload files** — drag and drop your own CSV files.\n\n"
        "Once files are selected you will see three green confirmations: files selected, files ready, and files loaded."
    ))
    _img("Step_1_Select_Default.png", _("Step 1 — Dataset selected; 5 files loaded and validated"))

    # ------------------------------------------------------------------ #
    # STEP 2 — File Validation & Preview                                   #
    # ------------------------------------------------------------------ #
    st.header(_("Step 2 — File Validation & Preview"))
    st.info(_(
        "The tool checks that every file has exactly **3 columns in order**: "
        "time (min) · temperature (°C) · mass (mg or %).\n\n"
        "A tabbed table shows the first rows of each file so you can confirm the data looks correct "
        "before proceeding. Each tab is named after the file."
    ))
    _img("step2.png", _("Step 2 — File preview showing the 3-column structure"))

    # ------------------------------------------------------------------ #
    # STEP 3 — Data Extraction                                             #
    # ------------------------------------------------------------------ #
    st.header(_("Step 3 — Data Extraction"))
    st.info(_(
        "Click **Extract Data**. The tool reads all files, converts temperatures to Kelvin, "
        "and prepares the data for analysis.\n\n"
        "A blue status message appears while processing, followed by a green confirmation "
        "listing every processed file."
    ))
    _img("step3.png", _("Step 3 — Data extraction completed successfully"))

    # ------------------------------------------------------------------ #
    # STEP 4 — Interactive Plots                                           #
    # ------------------------------------------------------------------ #
    st.header(_("Step 4 — Interactive Plots"))
    st.info(_(
        "Six interactive plots appear organised in tabs: TG, DTG, and dT/dt — each available "
        "against temperature (K) and against time (min).\n\n"
        "**TG (mass %)** shows sigmoidal mass-loss curves; higher heating rates (β) shift the "
        "curves to higher temperatures.\n\n"
        "**DTG** is the mass-loss rate; its peak marks the most active temperature zone. "
        "Use this peak to choose your conversion temperature range in Step 5.\n\n"
        "If needed, expand **Adjust curve x-ranges** to trim each curve individually — "
        "useful when files have different start and end temperatures."
    ))
    _img("step4.png", _("Step 4 — TG curves for all heating rates (temperature axis)"))
    _img("step4_ranges.png", _("Step 4 — x-range sliders to trim each curve independently"))

    # ------------------------------------------------------------------ #
    # STEP 5 — Conversion Analysis                                         #
    # ------------------------------------------------------------------ #
    st.header(_("Step 5 — Conversion Analysis"))
    st.info(_(
        "Click **Run Conversion**. The tool converts raw mass data into "
        "**α (conversion)**: 0 = reaction not started, 1 = reaction complete.\n\n"
        "One α(T) curve per file appears on a shared 0–1 scale. "
        "The Analysis Summary on the right confirms how many datasets were processed "
        "and the temperature range used for each one."
    ))
    _img("step5.png", _("Step 5 — Conversion α(T) curves for all heating rates"))

    # ------------------------------------------------------------------ #
    # STEP 6 — Isoconversion Analysis                                      #
    # ------------------------------------------------------------------ #
    st.header(_("Step 6 — Isoconversion Analysis"))
    st.info(_(
        "Isoconversion means comparing your experiments at the same conversion "
        "level α instead of the same time or temperature. At fixed α, the reaction "
        "rate depends only on temperature — the reaction model cancels out. That "
        "is what makes it possible to calculate E(α) in the next step without "
        "assuming any reaction model.\n\n"
        "Leave the **Conversion step size (Δα)** at the default `0.02` and click "
        "**Run Isoconversion**.\n\n"
        "The tool builds three tables — Temperature (K), Time (min), and Conversion Rate "
        "(Δα/Δt) — one row per α level, one column per heating rate. "
        "These tables are the numerical input to all five activation energy methods.\n\n"
        "Download any table as CSV with the button below it."
    ))
    _img("step6.png", _("Step 6 — Isoconversion temperature table (rows = α levels, columns = β)"))

    # ------------------------------------------------------------------ #
    # STEP 7 — Activation Energy Analysis                                  #
    # ------------------------------------------------------------------ #
    st.header(_("Step 7 — Activation Energy Analysis"))
    st.info(_(
        "Check one or more methods and click **Calculate Activation Energy**.\n\n"
        "- **Friedman, KAS, OFW** — fast differential/integral methods; good starting point.\n"
        "- **Vyazovkin (Vy) and Advanced Vyazovkin (aVy)** — iterative, slower, more accurate; "
        "set the **search bounds** for E (kJ/mol) to cover the expected range before running.\n\n"
        "The chart shows E(α) for every selected method with optional error bars. "
        "A flat curve means a simple single-step reaction; a varying curve indicates "
        "overlapping steps.\n\n"
        "Use the **active method selector** below the chart to choose which E(α) result "
        "feeds into Steps 8–10."
    ))
    _img("step7_settings.png", _("Step 7 — Method selection and Vy/aVy search bounds"))
    _img("step7_Activation_EnergyResults.png", _("Step 7 — E(α) results for all five methods"))

    # ------------------------------------------------------------------ #
    # STEP 8 — Pre-exponential Factor (Compensation Effect)                #
    # ------------------------------------------------------------------ #
    st.header(_("Step 8 — Pre-exponential Factor"))
    st.info(_(
        "Select a **reference heating rate** (any file works) and click "
        "**Calculate Compensation Effect**.\n\n"
        "The tool fits candidate reaction models to that file and uses the linear relationship "
        "between E and ln(A) to compute A(α) at every conversion level.\n\n"
        "The results panel shows the compensation line equation ln(A) = a·E + b, "
        "the number of accepted models, and the ln(A) vs α curve."
    ))
    _img("Step8.png", _("Step 8 — Compensation effect results and ln(A) vs α"))

    # ------------------------------------------------------------------ #
    # STEP 9 — Reaction Model Reconstruction                               #
    # ------------------------------------------------------------------ #
    st.header(_("Step 9 — Reaction Model Reconstruction"))
    st.info(_(
        "Select a **heating rate for temperature integration** and click **Reconstruct g(α)**.\n\n"
        "The tool numerically reconstructs the integral reaction model g(α) from your data — "
        "no model is assumed beforehand. "
        "Compare the shape of the curve to known theoretical models to identify the likely "
        "reaction mechanism. Download the reconstructed g(α) data as CSV."
    ))
    _img("Step9.png", _("Step 9 — Numerically reconstructed integral model g(α)"))

    # ------------------------------------------------------------------ #
    # STEP 10 — Kinetic Predictions                                        #
    # ------------------------------------------------------------------ #
    st.header(_("Step 10 — Kinetic Predictions"))
    st.info(_(
        "The kinetic triplet E(α), A(α), g(α) is now complete. "
        "Choose a prediction mode from the two tabs:\n\n"
        "- **Model-free Prediction** — uses E(α) and A(α) directly (no assumed model). "
        "Select **Isothermal** (constant temperature → α vs time) or "
        "**Linear heating** (constant rate → α vs temperature).\n"
        "- **Model-based Isothermal** — uses the full triplet including g(α).\n\n"
        "Enter the target temperature (K), the target final conversion α, and the time search "
        "bounds, then click **Run**. The result shows the predicted α(t) curve and the "
        "time to reach final conversion, with a downloadable CSV."
    ))
    _img("Step10_settings.png", _("Step 10 — Prediction inputs (isothermal model-free mode)"))
    _img("Step10_results.png", _("Step 10 — Predicted α(t) curve; final conversion reached at 131.98 min"))

    # ------------------------------------------------------------------ #
    # DONE                                                                 #
    # ------------------------------------------------------------------ #
    st.divider()
    st.success(_(
        "You have seen all 10 steps. "
        "Open the **Tool** page from the sidebar to run the analysis with your own data. "
        "Download your results with the buttons next to each table or plot."
    ))

    if st.button(_("Go to Tool"), key="walkthrough_go_to_tool"):
        st.switch_page("src/views/tool.py")


if __name__ == "__main__":
    main()
