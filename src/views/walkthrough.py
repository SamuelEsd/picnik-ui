"""
Walkthrough Tutorial View

Complete step-by-step guide covering all 10 steps of the pICNIK workflow.
"""

import streamlit as st
import base64
from pathlib import Path

from src.config import APP_TITLE, RESOURCES_DIR
from src.components.data_source import DataSourceSelector
from src.components.file_validation import (
    FileCountValidator,
    FileStructureValidator,
    FilePreview,
)


def main():
    """Full pICNIK walkthrough tutorial."""
    st.title(f"{APP_TITLE} — Tutorial")

    st.markdown(
        """
        This tutorial walks you through the complete **10-step pICNIK workflow** for analysing
        thermogravimetric (TGA) data and extracting kinetic parameters.

        > **What is TGA?**
        > Thermogravimetric Analysis (TGA) measures how the mass of a sample changes as it is
        > heated at a controlled rate. The result is a mass-vs-temperature (or mass-vs-time) curve
        > that reveals decomposition or reaction events.

        The pICNIK library uses data from several TGA experiments run at **different heating rates**
        (β, in K/min). By comparing how the same conversion degree is reached at different temperatures
        across experiments, you can extract the **activation energy E(α)** without assuming any
        reaction model — this is the *isoconversional principle*.
        """
    )

    # ------------------------------------------------------------------ #
    # STEP 1: Prepare files                                                #
    # ------------------------------------------------------------------ #
    st.header("Step 1 — Prepare Your Data Files")
    st.markdown(
        """
        pICNIK works with **CSV or DAT files** with exactly **3 columns**:

        | Column | Content | Units |
        |--------|---------|-------|
        | 1 | Time | min |
        | 2 | Temperature | °C |
        | 3 | Mass (or any thermally controlled property) | mg (or %) |

        You need **at least 2 files**, one per heating rate. More files (typically 3–6)
        give better statistics. Each file represents one TGA run at a different heating rate.

        **Example data sets included in the tool:**
        - `Constant_E` — simulated data with constant E = 75 kJ/mol, F1 reaction model
        - `Paracetamol` — real pharmaceutical decomposition data
        - `Decano` — real data for decane
        - `PolyProp` — polypropylene degradation
        - `Two_Steps` — simulated two-step reaction
        - `Variable_E` — simulated data with conversion-dependent E
        """
    )

    gif_path = RESOURCES_DIR / "download_example_files.gif"
    if gif_path.exists():
        with open(gif_path, "rb") as file_:
            contents = file_.read()
            data_url = base64.b64encode(contents).decode("utf-8")
            st.markdown(
                f'<img src="data:image/gif;base64,{data_url}" alt="download example">',
                unsafe_allow_html=True,
            )
    else:
        st.info("Example GIF not found. Use the default datasets or upload your own CSV files.")

    # ------------------------------------------------------------------ #
    # STEP 2: Load files                                                   #
    # ------------------------------------------------------------------ #
    st.header("Step 2 — Load Files")
    st.markdown(
        """
        Upload your CSV files below, or select one of the default example datasets.
        The library calls **`DataExtraction.read_files()`** internally, which:

        1. Reads each CSV into a pandas DataFrame
        2. Converts temperature from °C to Kelvin
        3. Computes mass-loss percentage `%m = 100 × (m / m₀)`
        4. Calculates the **heating rate β** via linear regression of T vs t
        5. Computes derivatives: `dT/dt` (temperature rate) and `dw/dt` (mass loss rate)
           using a Savitzky-Golay smoothing filter

        **Outputs:** an array of heating rates **B** [K/min] and initial temperatures **T₀** [K].
        """
    )

    data_source_selector = DataSourceSelector()
    file_paths = data_source_selector.render()
    if not file_paths:
        st.info("Select files to continue the tutorial.")
        return

    file_count_validator = FileCountValidator()
    if not file_count_validator.validate(file_paths):
        return

    file_structure_validator = FileStructureValidator()
    valid_files, invalid_files = file_structure_validator.validate(file_paths)
    if not valid_files:
        return

    file_preview = FilePreview()
    file_preview.render(valid_files, file_paths)

    # ------------------------------------------------------------------ #
    # STEP 3: Visualise experimental data                                  #
    # ------------------------------------------------------------------ #
    st.header("Step 3 — Visualise Experimental Data")
    st.markdown(
        """
        After loading, you can inspect your raw data through three plots on the **Tool** page:

        - **TG (Thermogravimetry):** mass % vs temperature or time — shows where the reaction occurs
        - **DTG (Derivative TG):** dm/dt vs temperature — highlights the peak reaction rate
        - **dT/dt:** temperature rate vs time — should be near-constant for a well-controlled experiment

        > **What to look for:**
        > For the `Constant_E` example you will see four parallel sigmoidal curves (one per heating rate)
        > in the TG plot. Higher β shifts the curve to higher temperatures — this is the kinetic
        > compensation effect in action.

        Use the **Extract Data** button on the Tool page to load the data and generate these plots.
        """
    )

    # ------------------------------------------------------------------ #
    # STEP 4: Conversion calculation                                       #
    # ------------------------------------------------------------------ #
    st.header("Step 4 — Conversion Calculation")
    st.markdown(
        r"""
        **Conversion α** represents the fraction of the reaction completed, from 0 (unreacted) to 1 (complete):

        $$\alpha = \frac{m_0 - m_t}{m_0 - m_\infty}$$

        where:
        - $m_0$ = initial mass
        - $m_t$ = mass at time t
        - $m_\infty$ = final residual mass

        You must set a **temperature range [Tᵢ, Tf]** that covers the reaction event. Use the TG plot
        to identify where mass starts and finishes changing.
        Calling `DataExtraction.Conversion(Ti, Tf)` clips each dataset to this range and computes α.

        > **Why does the range matter?**
        > If you include the flat regions before and after the reaction, α values outside 0–1 are
        > possible and the isoconversional tables become unreliable. Always zoom into the reaction event.
        """
    )

    # ------------------------------------------------------------------ #
    # STEP 5: Isoconversional tables                                       #
    # ------------------------------------------------------------------ #
    st.header("Step 5 — Isoconversional Tables")
    st.markdown(
        r"""
        The isoconversional principle states that for a given conversion α, the reaction rate depends
        **only on temperature**, not on the heating programme. This allows us to compare all experiments
        at the same conversion level.

        `DataExtraction.Isoconversion(d_a)` builds three tables indexed by conversion values
        (spaced by `d_a`):

        | Table | Contents |
        |-------|---------|
        | `TempAdvIsoDF` | Temperature (K) at each α for every heating rate |
        | `timeAdvIsoDF` | Time (min) at each α for every heating rate |
        | `diffAdvIsoDF` | Conversion rate dα/dt at each α for every heating rate |

        Each row is a **conversion level**; each column is a **heating rate**.
        This is the fundamental data structure for all activation energy methods.

        **Parameter `d_a`** controls the spacing between conversion values:
        - `d_a = 0.005` → ~200 rows (slow, precise)
        - `d_a = 0.02`  → ~50 rows (recommended default)
        - `d_a = 0.05`  → ~20 rows (fast, coarse)
        """
    )

    # ------------------------------------------------------------------ #
    # STEP 6: Activation Energy                                            #
    # ------------------------------------------------------------------ #
    st.header("Step 6 — Activation Energy Calculation")
    st.markdown(
        r"""
        The `ActivationEnergy` object is initialised with B, T₀ and the three isoconversional
        tables, then one of five methods is called.

        All methods return an array **E(α)** in kJ/mol — if E is constant across α, the reaction
        follows a single-step mechanism; if E varies, the mechanism is more complex.

        ### The five methods

        #### Friedman (Fr)
        Differential method. Linearises the rate equation:
        $$\ln\!\left(\frac{d\alpha}{dt}\right)_{\alpha,i} = \ln[A_\alpha f(\alpha)] - \frac{E_\alpha}{RT_{\alpha,i}}$$
        Most sensitive to noise; best when data quality is high.

        #### Ozawa-Flynn-Wall (OFW)
        Integral method. Linearises:
        $$\log \beta_i = C - \frac{0.4567\,E_\alpha}{RT_{\alpha,i}}$$
        Simple and robust; slight approximation bias at low α.

        #### Kissinger-Akahira-Sunose (KAS)
        Integral method. More accurate than OFW:
        $$\ln\!\left(\frac{\beta_i}{T_{\alpha,i}^2}\right) = C - \frac{E_\alpha}{RT_{\alpha,i}}$$

        #### Vyazovkin (Vy)
        Minimisation-based method. Finds E that minimises:
        $$\Omega(E_\alpha) = \sum_{i}\sum_{j \neq i} \frac{I[E_\alpha, T_{\alpha,i}]}{I[E_\alpha, T_{\alpha,j}]}$$
        No linear approximation — more accurate for strongly variable E.

        #### Advanced Vyazovkin (aVy)
        Improved Vy that integrates over a **time interval** instead of the full history.
        Controlled by parameter **p** (typically 0.5–0.99): higher p = narrower window = higher precision.
        Most rigorous method; computationally slowest.

        > **Which method to choose?**
        > Start with KAS or OFW for a quick estimate. Use aVy for publication-quality results.
        > Compare all five — if they agree, your data is good.
        """
    )

    # ------------------------------------------------------------------ #
    # STEP 7: Pre-exponential factor (Compensation Effect)                 #
    # ------------------------------------------------------------------ #
    st.header("Step 7 — Pre-exponential Factor via the Compensation Effect")
    st.markdown(
        r"""
        The **compensation effect** is the empirical linear relationship between activation energy
        and the logarithm of the pre-exponential factor across a family of reactions:

        $$\ln A = a + b\,E$$

        **How it is computed:**
        1. Several kinetic models f(α) are fitted to the experimental rate data at a reference heating rate
        2. Each model fit yields a pair (Eᵢ, Aᵢ)
        3. A linear regression over all (Eᵢ, ln Aᵢ) pairs gives the constants **a** and **b**
        4. The fitted line is evaluated at the isoconversional E(α) to obtain **ln A(α)**

        This gives you the **pre-exponential factor** A(α) as a function of conversion — the second
        element of the kinetic triplet (E, A, g(α)).

        > **Note:** The compensation effect is an experimental method that can be unreliable if
        > the model fits are poor. Always check that a reasonable number of models were accepted and
        > that the scatter plot shows a clear linear trend.
        """
    )

    # ------------------------------------------------------------------ #
    # STEP 8: Reaction model reconstruction                                #
    # ------------------------------------------------------------------ #
    st.header("Step 8 — Reaction Model Reconstruction — g(α)")
    st.markdown(
        r"""
        The **integral reaction model g(α)** describes the reaction mechanism. Common analytical
        forms include F1 (first-order), D3 (3D diffusion), A2 (Avrami-Erofeev), etc.

        Instead of assuming one of these, pICNIK **reconstructs g(α) numerically**:

        $$g(\alpha) = \sum_{i} A_{\alpha_i} \int_{t_{\alpha_{i-1}}}^{t_{\alpha_i}} \exp\!\left(-\frac{E_{\alpha_i}}{RT(t)}\right) dt$$

        The reconstructed curve is plotted alongside a library of analytical models. The shape of
        g(α) tells you the reaction mechanism:

        | Shape | Likely model |
        |-------|-------------|
        | Linear (slope ≈ 1) | F1 (first-order) |
        | Concave | Diffusion-controlled (D2, D3) |
        | Convex at start | Nucleation (A2, A3) |
        | S-shaped | Power-law (P2, P3) |

        This reconstructed g(α), together with E(α) and A(α), forms the complete **kinetic triplet**.
        """
    )

    # ------------------------------------------------------------------ #
    # STEP 9: Predictions                                                  #
    # ------------------------------------------------------------------ #
    st.header("Step 9 — Kinetic Predictions")
    st.markdown(
        r"""
        With the kinetic parameters in hand you can predict reaction behaviour under **any** temperature programme.

        ### Model-free prediction — `modelfree_prediction()`
        Based solely on E(α). Uses the equality of temperature integrals:

        $$J[E_\alpha, T(t)_i] = J[E_\alpha, T(t)_j]$$

        Given a new temperature programme T(t), the library finds the time t required to match the
        integral at each conversion level. Three modes:

        | Mode | Description | Parameters |
        |------|-------------|-----------|
        | **Isothermal** | Hold at constant T | `isoT = 575` K |
        | **Linear heating** | Ramp at β K/min | `B = 10` K/min |
        | **Custom** | Arbitrary T(t) function | `T_func = my_func` |

        ### Model-based prediction — `t_isothermal()`
        Uses the full kinetic triplet (E, A, g(α)):

        $$t_\alpha = \frac{g(\alpha)}{A \exp(-E / RT)}$$

        This is more accurate for interpolation near the experimental conditions but requires a
        valid g(α) from Step 8.

        > **Bounds parameter:**
        > The prediction involves a minimisation at each conversion step. The `bounds` tuple sets
        > the search window in minutes — e.g., `(10, 10)` searches ±10 min around the previous
        > time point. Set bounds to the expected order of magnitude of the total process duration.
        """
    )

    # ------------------------------------------------------------------ #
    # STEP 10: Export results                                              #
    # ------------------------------------------------------------------ #
    st.header("Step 10 — Export Results")
    st.markdown(
        """
        Every step in the Tool page has download buttons that export results as CSV files:

        | Export | File | Contents |
        |--------|------|---------|
        | Activation energy | `activation_energy_<method>.csv` | α, E, error |
        | Isoconversion tables | `isoconversion_temperature.csv` etc. | T, t, dα/dt tables |
        | Compensation effect | `compensation_effect_lnA.csv` | α, ln(A), error |
        | Model reconstruction | `reaction_model_g_alpha.csv` | α, g(α) |
        | Model-free prediction | `modelfree_prediction_<mode>.csv` | time, T, α |
        | Model-based prediction | `isothermal_prediction_<T>K.csv` | time, α |

        The library also provides `export_kinetic_triplet()` which bundles E, ln(A) and g(α)
        into a single file — useful for archiving or sharing results.
        """
    )

    st.success(
        "You are ready to use the **Tool** page for your own analysis. "
        "Follow the steps in order: Extract → Conversion → Isoconversion → "
        "Activation Energy → Compensation Effect → Reconstruction → Predictions."
    )


if __name__ == "__main__":
    main()
