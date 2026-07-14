import streamlit as st
from src.config import RESOURCES_DIR
from src.i18n import _


def show():
    st.title(_("pICNIK Web UI"), anchor=False)
    st.markdown(
        _(
            "A web interface for [**pICNIK**](https://pypi.org/project/picnik/), "
            "an open-source Python library for isoconversional kinetic analysis of "
            "thermogravimetric (TGA) data.\n\n"
            "Upload your TGA files, run the analysis step by step, and download the results — "
            "no Python required."
        )
    )


def show_description():
    st.subheader(_("What you can do"), anchor=False)
    st.markdown(
        _(
            "- Compute the **activation energy E(α)** using five established methods "
            "(Friedman, OFW, KAS, Vyazovkin, Advanced Vyazovkin)\n"
            "- Obtain the **pre-exponential factor A(α)** via the compensation effect\n"
            "- Reconstruct the **reaction model g(α)** from your data\n"
            "- Generate **isothermal and non-isothermal predictions** for any temperature programme\n"
            "- Export all results as **CSV files** and publication-ready **PNG plots**\n"
            "- Switch the interface between **Spanish and English**"
        )
    )

    st.divider()
    st.subheader(_("The kinetic triplet"), anchor=False)
    st.markdown(
        _(
            "Every pICNIK analysis produces three parameters that together fully describe the "
            "reaction kinetics. Once you have them, you can predict how much of the material "
            "will have reacted at any temperature and time."
        )
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            _(
                '<div style="border-left: 4px solid #1f77b4; padding-left: 12px; margin-bottom: 8px">\n\n'
                "**E(α) — Activation energy**\n\n"
                "The energy barrier the reaction must overcome at each conversion level. "
                "Units: kJ/mol. A constant E means a simple single-step process; "
                "a varying E indicates overlapping steps.\n\n"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            _(
                '<div style="border-left: 4px solid #ff7f0e; padding-left: 12px; margin-bottom: 8px">\n\n'
                "**A(α) — Pre-exponential factor**\n\n"
                "How frequently molecules attempt to overcome the barrier, per minute. "
                "Obtained from E(α) via the compensation effect — no reaction model assumed.\n\n"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            _(
                '<div style="border-left: 4px solid #2ca02c; padding-left: 12px; margin-bottom: 8px">\n\n'
                "**g(α) — Reaction model**\n\n"
                "Describes how the conversion rate depends on how much has already reacted. "
                "Reconstructed numerically from your data — no model assumed beforehand.\n\n"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    st.divider()
    st.subheader(_("What the tool needs"), anchor=False)
    st.markdown(
        _(
            "pICNIK requires **multiple TGA experiments run at different heating rates** "
            "(at least 2, ideally 4–5). Each experiment is one CSV file with three columns: "
            "time, temperature, and mass.\n\n"
            "Comparing the same conversion level across experiments at different heating rates "
            "is what allows the tool to extract E(α) without ever assuming which reaction model applies."
        )
    )

    st.divider()
    st.subheader(_("Why isoconversion works"), anchor=False)
    st.markdown(
        _(
            "The isoconversional principle states that at a fixed conversion level α, "
            "the reaction rate depends only on temperature — not on the reaction "
            "model. Comparing the same α across experiments run at different heating "
            "rates isolates that temperature dependence, which is exactly what Step 6 "
            "does before computing E(α) in Step 7.\n\n"
            "This is why these methods are called \"model-free\": they don't skip the "
            "reaction model, they just avoid having to guess it before calculating the "
            "activation energy."
        )
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(
            str(RESOURCES_DIR / "Figures" / "Figure_01.png"),
            caption=_("TGA mass loss and conversion α"),
            width=700,
        )

    st.divider()
    st.subheader(_("Further reading"), anchor=False)
    st.markdown(
        _(
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
                "New to isoconversional analysis? Start here. "
                "The Tutorial walks you through all 10 steps with instructions on what to do and what to expect."
            )
        )
        if st.button(_("Go to Tutorial"), key="home_btn_tutorial"):
            st.switch_page("src/views/walkthrough.py")
    with col2:
        st.markdown(_("### 2. Tool"))
        st.write(
            _(
                "Upload your TGA CSV files and run the full analysis: "
                "extraction, conversion, isoconversion, activation energy, "
                "compensation effect, reconstruction, and predictions."
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
