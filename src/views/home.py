import streamlit as st
from src.config import RESOURCES_DIR
from src.i18n import _


def show():
    st.title(_("pICNIK Web UI"), anchor=False)
    st.markdown(
        _(
            "A web interface for [**pICNIK**](https://pypi.org/project/picnik/) "
            "(*Python package for Isoconversional Computations for Non-Isothermal Kinetics*), "
            "an open-source Python library for isoconversional kinetic analysis.\n\n"
            "Its purpose is to study the dependence on time and temperature of thermally stimulated "
            "processes, including:\n\n"
            "- Shelf life of pharmaceutical compounds\n"
            "- Thermal stability of materials\n"
            "- Phase transitions\n"
            "- Spin crossover\n"
            "- Desorption of nanoconfined fluids\n\n"
            "These processes can be monitored under controlled temperature programs with techniques such as "
            "thermogravimetric analysis (TGA), differential scanning calorimetry (DSC), and SQUID "
            "magnetometry. pICNIK is designed to work with thermogravimetric data, but it can also process "
            "SQUID magnetometry data and DSC data in its cumulative form or when the conversion degree has "
            "already been calculated beforehand."
        )
    )

    st.markdown(
        _(
            "pICNIK normalises the measured signal into **α (conversion)**, "
            "a dimensionless number from 0 to 1:"
        )
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(
            str(RESOURCES_DIR / "Figures" / "Figure_01.png"),
            caption=_("TGA mass loss and conversion α"),
            width=700,
        )

    st.markdown(
        _(
            "Every computation in pICNIK is expressed as a function of α — not time or temperature\n"
            "directly. This makes results comparable across different heating rates."
        )
    )


def show_description():
    st.subheader(_("What pICNIK does"), anchor=False)
    st.markdown(
        _(
            "pICNIK analyses a set of measurements — each run at a **different heating rate** — "
            "to answer one practical question:\n\n"
            "> *How much of this material will have reacted at any given temperature and time —\n"
            "> whether in an industrial furnace, a storage facility, or a laboratory reactor?*\n\n"
            "To make that prediction you need three parameters that together fully describe the reaction "
            "kinetics. They are called the **kinetic triplet**:"
        )
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            _(
                '<div style="border-left: 4px solid #1f77b4; padding-left: 12px; margin-bottom: 8px">\n\n'
                "**E(α) — Activation energy**\n\n"
                "The energy barrier molecules must overcome to react, at each conversion level.\n"
                "Units: kJ/mol.\n\n"
                "A high-E reaction is nearly dormant at low temperatures and then\n"
                "accelerates steeply once enough thermal energy is available. The transition from\n"
                '\"barely reacting\" to \"reacting fast\" happens over a much narrower temperature window\n'
                "than for a low-E reaction.\n\n"
                "            </div>"
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            _(
                '<div style="border-left: 4px solid #ff7f0e; padding-left: 12px; margin-bottom: 8px">\n\n'
                "**A(α) — Pre-exponential factor**\n\n"
                "The rate at which molecules in the bulk sample attempt to react, per minute.\n"
                "Units: 1/min.\n\n"
                "Each molecule crosses the energy barrier only once — after that it has reacted\n"
                "and is gone. But a solid sample contains ~10²³ molecules all attempting\n"
                "independently and simultaneously. **A** captures how frequently those attempts\n"
                "occur across the whole population. A higher **A** means more attempts per minute,\n"
                "so more reactions succeed per unit time even if the barrier stays the same.\n\n"
                "Obtained from E(α) via the compensation effect.\n\n"
                "            </div>"
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            _(
                '<div style="border-left: 4px solid #2ca02c; padding-left: 12px; margin-bottom: 8px">\n\n'
                "**g(α) — Reaction model**\n\n"
                "The integral expression of the reaction model f(α). It arises from proposing "
                "a physicochemical model for the process: nucleation and growth, diffusion, "
                "geometrical contraction, and others. Different models are suited to different "
                "processes and can be found in the literature (Vyazovkin, 2015). "
                "pICNIK includes 34 reaction models in its rxn_models complement and "
                "reconstructs g(α) numerically from the experimental data.\n\n"
                "            </div>"
            ),
            unsafe_allow_html=True,
        )

    st.markdown(
        _(
            "The general kinetic equation that relates all three:\n\n"
            "> **dα/dt = A(α) · exp(−E(α) / RT) · f(α)**\n\n"
            "Once the triplet is known, you can predict how much of the material will have reacted "
            "at any temperature and time — whether in an industrial furnace, a storage facility, "
            "or a laboratory reactor."
        )
    )

    st.divider()
    st.subheader(_("Why multiple heating rates?"), anchor=False)
    st.markdown(
        _(
            "The **isoconversional principle** is the mathematical foundation of pICNIK. It states that\n"
            "at a fixed conversion α, the reaction rate depends *only* on temperature — not on how the\n"
            "sample was heated to get there. This means that by comparing the same conversion level\n"
            "across experiments run at different heating rates, it is possible to extract the activation\n"
            "energy **without ever assuming which reaction model applies**.\n\n"
            "With just one heating rate you cannot separate E from the reaction model. You need at least\n"
            "3 experiments, ideally 4–5, spanning a reasonable range (e.g., 5, 10, 15, 20 K/min).\n\n"
            "**Analogy:** imagine runners completing a race at different speeds (heating rates).\n"
            "They each reach the 50% checkpoint at different times — but if you compare *what the\n"
            "terrain looks like at that exact checkpoint* across all runners, you can figure out\n"
            "how steep the hill is (activation energy) without ever needing to know each runner's\n"
            "personal style (reaction model). The checkpoint is α; the hill steepness is E."
        )
    )

    st.divider()
    st.subheader(_("The mathematical foundation"), anchor=False)
    st.markdown(
        _(
            "Everything in pICNIK is built on one equation. The speed of any thermally-activated\n"
            "reaction follows the **Arrhenius equation**:\n\n"
            "> **k(T) = A · exp(−E / RT)**\n\n"
            "where k is the reaction rate constant, T is temperature in Kelvin, and\n"
            "R = 0.008314 kJ/(mol·K). For a solid decomposing under a temperature program, this\n"
            "becomes the **general rate equation**:\n\n"
            "> **dα/dt = A · exp(−E / RT) · f(α)**\n\n"
            "This single equation contains all three elements of the kinetic triplet. The three\n"
            "unknowns — E, A, and f(α) — cannot be determined from a single experiment. pICNIK's\n"
            "entire workflow is a systematic strategy to extract all three from a set of TGA runs\n"
            "at different heating rates, without ever assuming which reaction model f(α) applies."
        )
    )

    st.divider()
    st.subheader(_("The analysis workflow"), anchor=False)
    st.markdown(
        _(
            "```\n"
            "Raw TGA files  (one CSV per heating rate)\n"
            "        │\n"
            "        ▼\n"
            "1. Read & clean data        →  heating rates β, initial temperatures T₀\n"
            "        │\n"
            "        ▼\n"
            "2. Compute conversion α     →  α(T) curves, 0 = unreacted · 1 = complete\n"
            "        │\n"
            "        ▼\n"
            "3. Build isoconversion tables  →  T, t, dα/dt  at fixed α values across all runs\n"
            "        │\n"
            "        ▼\n"
            "4. Compute activation energy E(α)  →  five methods: Fr, OFW, KAS, Vy, aVy\n"
            "        │\n"
            "        ▼\n"
            "5. Compensation effect      →  obtain ln A(α) from E(α)\n"
            "        │\n"
            "        ▼\n"
            "6. Reconstruct reaction model g(α)  →  numerical, no model assumed\n"
            "        │\n"
            "        ▼\n"
            "7. Predict behavior         →  at any constant or programmed temperature\n"
            "```"
        )
    )

    st.divider()
    st.subheader(_("Five activation energy methods"), anchor=False)
    st.markdown(
        _(
            "pICNIK computes E(α) using five established isoconversional methods:"
        )
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            _(
                "- **Fr — Friedman**: differential, most sensitive, highest accuracy when data is clean\n"
                "- **OFW — Ozawa-Flynn-Wall**: integral, simple, slight approximation bias\n"
                "- **KAS — Kissinger-Akahira-Sunose**: integral, better approximation than OFW"
            )
        )
    with col2:
        st.markdown(
            _(
                "- **Vy — Vyazovkin**: numerical optimisation, no approximation, handles variable E well\n"
                "- **aVy — Advanced Vyazovkin**: most rigorous, incremental integration, best for complex reactions"
            )
        )

    st.info(
        _(
            "If all five methods agree, your data is consistent and the result is reliable. "
            "If they diverge, use aVy as the reference — it makes the fewest assumptions."
        )
    )


    st.divider()
    st.subheader(_("Further reading"), anchor=False)
    st.markdown(
        _(
            "For more information on the theoretical basis of isoconversional kinetic analysis, "
            "we recommend consulting the following sources:\n\n"
            "- Vyazovkin, S. (2015). *Isoconversional kinetics of thermally stimulated processes*. "
            "Springer International Publishing. https://doi.org/10.1007/978-3-319-14175-6\n"
            "- Ramírez, E., Balmaseda, J., & Torres-García, E. (2022). pICNIK: Python package with "
            "isoconversional computations for non-isothermal kinetics. "
            "*Computer Physics Communications*, 278, 108416."
        )
    )


def show_workflow():
    st.divider()
    st.subheader(_("Get started"), anchor=False)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(_("### 1. Tutorial"))
        st.write(
            _(
                "Step-by-step guide with theory, formulas, and worked examples. "
                "Start here if you are new to isoconversional analysis."
            )
        )
        if st.button(_("Go to Tutorial"), key="home_btn_tutorial"):
            st.switch_page("src/views/walkthrough.py")
    with col2:
        st.markdown(_("### 2. Tool"))
        st.write(
            _(
                "Upload your TGA CSV files and run the full analysis: extraction, conversion, "
                "isoconversion, activation energy, compensation effect, reconstruction, and predictions."
            )
        )
        if st.button(_("Go to Tool"), key="home_btn_tool"):
            st.switch_page("src/views/tool.py")
    with col3:
        st.markdown(_("### 3. Export"))
        st.write(
            _(
                "Download results as CSV files directly from the Tool page after each step. "
                "Every computed table and curve can be exported."
            )
        )


show()
show_description()
show_workflow()
