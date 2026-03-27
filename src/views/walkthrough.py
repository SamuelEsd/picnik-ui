"""
Walkthrough Tutorial View

Complete step-by-step guide covering all 10 steps of the pICNIK workflow,
including the theory behind each step, how to use the tool, and a FAQ section.
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

        Each step explains **what** it does, **why** it is necessary, and **how** to use it in the tool.
        Expand the *Theory* section under each step to see the underlying mathematics.
        """
    )

    # ------------------------------------------------------------------ #
    # BIG PICTURE                                                          #
    # ------------------------------------------------------------------ #
    st.header("The Big Picture")
    st.markdown(
        """
        A **TGA experiment** places a tiny solid sample in a furnace, heats it at a controlled rate
        (for example 10 °C/min), and continuously measures its mass. As the material decomposes,
        gases escape and the mass drops. The instrument records three columns:

        | Column | Content | Units |
        |--------|---------|-------|
        | 1 | Time | min |
        | 2 | Temperature | °C |
        | 3 | Mass | mg (or %) |

        That is all pICNIK needs. The goal is to extract the **kinetic triplet** from this data:

        | Symbol | Name | Meaning |
        |--------|------|---------|
        | **E(α)** | Activation energy | Energy barrier the reaction must overcome, at each conversion level |
        | **A(α)** | Pre-exponential factor | How often molecules attempt to overcome that barrier |
        | **f(α) / g(α)** | Reaction model | How the rate depends on how much has already reacted |

        Once you have the kinetic triplet, you can **predict conversion at any temperature and time**
        condition — whether in a furnace, a storage tank, or a reactor.
        """
    )

    with st.expander("Theory — the isoconversional principle"):
        st.markdown(
            r"""
            ### Why you need multiple heating rates

            The general rate equation for a solid-state reaction is:

            $$\frac{d\alpha}{dt} = A \cdot \exp\!\left(-\frac{E}{RT}\right) \cdot f(\alpha)$$

            This equation has three unknowns: E, A, and f(α). With a single experiment you cannot
            separate them — there are infinitely many combinations of E, A, and f(α) that fit one curve.

            The **isoconversional principle** solves this. It states:

            > *At a fixed conversion α, the reaction rate depends only on temperature — regardless of
            > what heating programme was used to get there.*

            Mathematically, if you hold α constant and compare across different experiments
            (different heating rates β), the term f(α) is the same constant for all of them.
            Dividing two experiments at the same α cancels f(α) completely, leaving only E and T.
            This means E can be determined **without ever assuming a reaction model**.

            This is why you need at least 3 experiments at different heating rates: to observe
            the same conversion α at different temperatures. More heating rates (4–5 recommended)
            give smaller confidence intervals.

            ### The Arrhenius equation

            The temperature dependence of reaction rates follows the **Arrhenius equation** (1889):

            $$k(T) = A \cdot \exp\!\left(-\frac{E}{RT}\right)$$

            - **k(T)** — reaction rate constant at temperature T
            - **A** — pre-exponential factor (frequency factor), units 1/min
            - **E** — activation energy (energy barrier), kJ/mol
            - **R** — universal gas constant, 0.008314 kJ/(mol·K)
            - **T** — absolute temperature in Kelvin

            Think of E as a hill. Molecules can only react if they have enough energy to climb it.
            Higher temperature gives more molecules that energy, so the reaction is faster.
            A tells you how many molecules are attempting to climb per minute.
            """
        )

    # ------------------------------------------------------------------ #
    # STEP 1: Prepare files                                                #
    # ------------------------------------------------------------------ #
    st.header("Step 1 — Prepare Your Data Files")
    st.markdown(
        """
        **What:** Organise your TGA output files — one CSV per heating rate experiment.

        **Why:** pICNIK needs multiple experiments to apply the isoconversional principle. Each file
        is one run at a different heating rate β. You need at least 2 files; 4–5 is recommended
        for reliable statistics.

        **How:** Each CSV must have exactly **3 columns** in this order:

        | Column | Content | Units |
        |--------|---------|-------|
        | 1 | Time | min |
        | 2 | Temperature | °C |
        | 3 | Mass (or any thermally controlled property) | mg (or %) |

        **Example datasets included in the tool:**
        - `Constant_E` — simulated data, E = 75 kJ/mol, F1 reaction model
        - `Paracetamol` — real pharmaceutical decomposition
        - `Decano` — real data for decane
        - `PolyProp` — polypropylene degradation
        - `Two_Steps` — simulated two-step reaction
        - `Variable_E` — simulated data with conversion-dependent E
        """
    )

    with st.expander("Theory — why heating rate matters"):
        st.markdown(
            r"""
            The **nominal heating rate β** (e.g., "10 K/min") is printed on the instrument panel,
            but real instruments deviate slightly from the programmed value. pICNIK computes the
            actual β by fitting a straight line to the Temperature-vs-time data via linear regression.
            The slope of that line is the true β used in all subsequent calculations.

            Higher β shifts the conversion curve to higher temperatures: the sample "doesn't have
            time" to react at lower temperatures when heated quickly. This shift is exactly what
            the isoconversional analysis exploits. The experiments should span a meaningful range —
            e.g., 5, 10, 15, 20 K/min — with at least a factor of 2 between the slowest and fastest.
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
        **What:** Upload your CSV files (or select a default dataset). pICNIK reads each file,
        validates its structure, and computes derived quantities.

        **Why:** Raw TGA files contain temperature in °C and absolute mass in mg. Before any
        kinetic analysis, these must be converted to consistent units and derivatives must be computed.

        **How:** Select files below. The library calls `DataExtraction.read_files()` internally, which:

        1. Reads each CSV into a table
        2. Converts temperature from °C to Kelvin
        3. Computes mass-loss percentage: `%m = 100 × (m / m₀)`
        4. Calculates the actual heating rate β via linear regression of T vs t
        5. Computes `dT/dt` and `dw/dt` (mass loss rate) using a Savitzky-Golay smoothing filter

        **Outputs:** an array of heating rates **B** [K/min] and initial temperatures **T₀** [K].
        """
    )

    with st.expander("Theory — Savitzky-Golay derivatives"):
        st.markdown(
            r"""
            TGA data is inherently noisy. Computing derivatives (dT/dt, dw/dt) naively with finite
            differences would amplify that noise catastrophically — every small measurement fluctuation
            becomes a large spike in the derivative.

            The **Savitzky-Golay filter** solves this by fitting a local polynomial through a window
            of neighbouring data points (e.g., 5 or 11 points), then evaluating the derivative of
            that polynomial at the centre point. The result is smooth and physically meaningful because
            it respects the local shape of the curve without being sensitive to individual point noise.

            This filter is used twice: once here for the DTG curve, and again in Step 4 when computing
            the conversion rate dα/dt needed by the Friedman method.
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
        **What:** Inspect the raw TGA curves before any kinetic analysis.

        **Why:** Visual inspection lets you identify the reaction region, check for multiple
        decomposition steps, and detect any problematic experiments (bad baseline, noise, outliers).

        **How:** Use the **Extract Data** button on the Tool page to load the data. Three plots appear:

        - **TG (Thermogravimetry):** mass % vs temperature — shows where the reaction occurs
        - **DTG (Derivative TG):** dm/dt vs temperature — peaks mark the most active decomposition zones
        - **dT/dt:** temperature rate vs time — should be near-constant for a well-controlled experiment

        > For the `Constant_E` example you will see four parallel sigmoidal curves (one per heating
        > rate) in the TG plot. Higher β shifts the curve to higher temperatures — this is the
        > isoconversional effect in action.
        """
    )

    with st.expander("Theory — what the curves tell you"):
        st.markdown(
            r"""
            The **TG curve** shows the normalised mass as a function of temperature. A flat region
            means no reaction is occurring. A steep descent indicates active decomposition.

            The **DTG curve** is the first derivative of the TG curve with respect to temperature
            (or time). Its peaks correspond to the temperatures of maximum reaction rate. If you see
            two peaks, there are at least two overlapping decomposition steps — you will need to
            select a temperature window (Step 4) that isolates one of them.

            The **dT/dt plot** confirms the linearity of the heating programme. If the heating rate
            is not constant (e.g., initial lag phase), this will appear here. Only the linear portion
            is used in kinetic analysis.
            """
        )

    # ------------------------------------------------------------------ #
    # STEP 4: Conversion calculation                                       #
    # ------------------------------------------------------------------ #
    st.header("Step 4 — Conversion Calculation")
    st.markdown(
        r"""
        **What:** Convert raw mass data into the dimensionless quantity α (conversion), ranging from
        0 (reaction not started) to 1 (reaction complete), over a user-selected temperature window.

        **Why:** Raw mass in mg depends on how much sample was loaded and what fraction remains as
        residue — these vary between runs. Conversion α normalises everything to a universal 0–1 scale
        that is comparable across experiments and required by the kinetic equations.

        **How:** On the Tool page, use the temperature range slider to select [Tᵢ, Tf] — the window
        that contains the reaction of interest. Then click **Compute Conversion**.

        The formula used is:

        $$\alpha = \frac{m_0 - m_t}{m_0 - m_\infty}$$

        where m₀ is the mass at Tᵢ, m_t is the current mass, and m_∞ is the mass at Tf.

        > **Tip:** use the DTG plot to find the reaction boundaries. Set Tᵢ just before the DTG
        > peak rises from baseline, and Tf just after it returns to baseline.
        """
    )

    with st.expander("Theory — from TG(%) to conversion α"):
        st.markdown(
            r"""
            ### TG(%) — the instrument output

            The TGA instrument records mass in milligrams. Before pICNIK, the instrument normalises
            this to a percentage of the initial mass:

            $$\text{TG}(\%) = \frac{m}{m_0} \times 100$$

            A fresh, unreacted sample starts at TG(%) = 100 and falls to a residual value (e.g., 30%)
            when the reaction is complete.

            ### Why TG(%) is not enough

            TG(%) still depends on what you define as "complete." Different experiments may have
            slightly different baselines. More importantly, the kinetic equations require a quantity
            that goes cleanly from exactly 0 to exactly 1, starting precisely when the reaction begins
            and ending when it finishes.

            ### Conversion α — the normalised version

            Selecting the window [T₀, Tf] and applying:

            $$\alpha(T) = \frac{m(T_0) - m(T)}{m(T_0) - m(T_f)}$$

            gives α = 0 at T₀ (reaction start) and α = 1 at Tf (reaction complete), regardless of
            sample size or residue fraction.

            ### The conversion rate dα/dt

            pICNIK also computes the rate of conversion numerically:

            $$\frac{d\alpha}{dt} \approx \text{Savitzky-Golay derivative of } \alpha(t)$$

            This rate is needed by the Friedman method (Step 6). The same smoothing filter described
            in Step 2 is used to avoid noise amplification.
            """
        )

    # ------------------------------------------------------------------ #
    # STEP 5: Isoconversional tables                                       #
    # ------------------------------------------------------------------ #
    st.header("Step 5 — Isoconversional Tables")
    st.markdown(
        r"""
        **What:** Build three tables that record, for each conversion level α and each heating rate,
        the temperature T, time t, and conversion rate dα/dt at which that conversion was reached.

        **Why:** The raw data from each experiment is recorded at regular time intervals — not at
        regular α values. To apply the isoconversional principle, you need exactly the same α values
        across all experiments. These tables extract and align that information.

        **How:** Click **Compute Isoconversion** on the Tool page. The parameter `d_a` controls the
        spacing between conversion values:

        | d_a | Number of rows | Speed |
        |-----|---------------|-------|
        | 0.005 | ~200 | Slow, precise |
        | 0.02 | ~50 | Default (recommended) |
        | 0.05 | ~20 | Fast, coarse |

        **The three tables produced:**

        | Table | Contents |
        |-------|---------|
        | `TempAdvIsoDF` | Temperature (K) at each α for every heating rate |
        | `timeAdvIsoDF` | Time (min) at each α for every heating rate |
        | `diffAdvIsoDF` | Conversion rate dα/dt at each α for every heating rate |

        Each row is a conversion level; each column is a heating rate. These tables are the input
        to all five activation energy methods.
        """
    )

    with st.expander("Theory — interpolation and the Advanced tables"):
        st.markdown(
            r"""
            ### Why interpolation is needed

            Experiments record data at regular time steps (e.g., every 0.5 s). At those time steps,
            α takes irregular values (e.g., 0.0312, 0.0578, ...). To compare experiments at the same
            α (e.g., exactly α = 0.30), values must be interpolated.

            pICNIK uses **cubic spline interpolation** to estimate T, t, and dα/dt at each exact
            α grid point. Cubic splines are smooth, pass through every data point, and have continuous
            first and second derivatives — making them well-suited for this application.

            ### Standard vs Advanced tables

            pICNIK generates two sets of tables:

            - **Standard** (`TempIsoDF`, `timeIsoDF`, `diffIsoDF`): evenly spaced at the user-specified
              d_a. Used by Fr, OFW, KAS, and Vy.
            - **Advanced** (`TempAdvIsoDF`, `timeAdvIsoDF`, `diffAdvIsoDF`): more finely spaced and
              optimised for small Δα intervals. Required by the Advanced Vyazovkin (aVy) method, which
              integrates over incremental α windows.
            """
        )

    # ------------------------------------------------------------------ #
    # STEP 6: Activation Energy                                            #
    # ------------------------------------------------------------------ #
    st.header("Step 6 — Activation Energy Calculation")
    st.markdown(
        r"""
        **What:** Compute the activation energy E as a function of conversion α using up to five
        isoconversional methods.

        **Why:** E(α) is the central result of the analysis. If E is constant across α, the reaction
        follows a simple single-step mechanism. If E varies, the process has overlapping steps with
        different barriers. Comparing all five methods reveals whether your data is internally
        consistent and how reliable the result is.

        **How:** On the Tool page, select the method(s) and click **Compute Activation Energy**.
        Results are plotted as E(α) curves with error bars.

        > **Which method?** Use KAS or OFW for a quick estimate. Use aVy for publication-quality
        > results. If all five agree (within error bars), your data is excellent.
        """
    )

    with st.expander("Theory — the five methods in detail"):
        st.markdown(
            r"""
            All five methods are derived from the same general rate equation:

            $$\frac{d\alpha}{dt} = A \cdot \exp\!\left(-\frac{E}{RT}\right) \cdot f(\alpha)$$

            They differ in how they manipulate this equation to isolate E.

            ---

            ### Friedman (Fr) — differential, most direct

            Take the natural log of the rate equation:

            $$\ln\!\left(\frac{d\alpha}{dt}\right)_{\alpha,i} = \ln[A \cdot f(\alpha)] - \frac{E_\alpha}{R \cdot T_{\alpha,i}}$$

            At fixed α, the term ln[A·f(α)] is a constant. So plotting ln(dα/dt) vs 1/T across
            all heating rates at the same α gives a straight line with slope = −E/R.

            **Pros:** Uses the instantaneous rate — most direct, no approximation.
            **Cons:** Very sensitive to noise in dα/dt. If the derivative data is noisy, Fr will
            show high scatter.

            ---

            ### Ozawa-Flynn-Wall (OFW) — integral, simple

            Integrating the rate equation with respect to temperature and applying the **Doyle
            approximation** to the integral:

            $$\ln \beta_i = C - \frac{1.052 \cdot E_\alpha}{R \cdot T_{\alpha,i}}$$

            Plot ln(β) vs 1/T at fixed α. Slope gives E via the factor R/1.052.

            **Pros:** Integral form is robust to noise.
            **Cons:** The Doyle approximation introduces a systematic bias (typically ~1–3 kJ/mol).

            ---

            ### Kissinger-Akahira-Sunose (KAS) — integral, more accurate

            Uses the better **Coats-Redfern approximation** p(x) ≈ exp(−x)/x²:

            $$\ln\!\left(\frac{\beta_i}{T_{\alpha,i}^2}\right) = C - \frac{E_\alpha}{R \cdot T_{\alpha,i}}$$

            **Pros:** More accurate than OFW. Still computationally cheap.
            **Cons:** Still an approximation. pICNIK uses T^1.92 (a slight refinement over T^2).

            ---

            ### Vyazovkin (Vy) — minimisation, no approximation

            Instead of approximating the temperature integral, Vy computes it numerically and finds
            E by minimisation. Define:

            $$\Omega(E_\alpha) = \sum_i \sum_{j \neq i} \frac{I(E_\alpha, T_{\alpha,i})}{I(E_\alpha, T_{\alpha,j})}$$

            where I(E, T) = ∫ exp(−E/RT) dT / β from T₀ to T_α. The isoconversional principle says
            that for the correct E, all ratios should equal 1 and Ω is minimised.

            pICNIK uses `scipy.optimize.minimize_scalar` for each α row. Integration is done via
            the Senum-Yang rational approximation by default (fast and accurate).

            **Pros:** No approximation error. Handles variable E well.
            **Cons:** Assumes linear heating from T₀. More expensive than Fr/OFW/KAS.

            ---

            ### Advanced Vyazovkin (aVy) — most rigorous

            Vy integrates from T₀ to T_α — mixing all E values from the start to the current
            conversion. If E varies strongly with α, this introduces error.

            aVy fixes this by integrating over **small incremental windows** Δα:

            $$\Omega(E_\alpha) = \sum_i \sum_{j \neq i} \frac{J(E_\alpha,\, t_{\alpha,i})}{J(E_\alpha,\, t_{\alpha,j})}$$

            where J is integrated over real time using the measured T(t) profile — no assumption
            of linear heating.

            **Pros:** Most rigorous. Each E value is local to a narrow α window. Works with
            arbitrary temperature programmes.
            **Cons:** Most computationally expensive.

            ---

            ### Error estimation

            - **Fr, OFW, KAS:** confidence interval from the standard error of the linear regression slope.
            - **Vy, aVy:** based on the F-distribution. The variance S²(E) of the ratios I_i/I_j
              is computed. The 95% confidence limits are the E values where S²(E)/S²(E_min) equals
              the F-critical value for n−1 degrees of freedom.

            | Method | Type | Approx? | Noise sensitivity | Cost |
            |--------|------|---------|------------------|------|
            | Fr | Differential | None | High | Low |
            | OFW | Integral | Doyle (coarse) | Low | Low |
            | KAS | Integral | Coats-Redfern (good) | Low | Low |
            | Vy | Integral + optimise | None | Low | Medium |
            | aVy | Incremental + optimise | None | Low | High |
            """
        )

    # ------------------------------------------------------------------ #
    # STEP 7: Pre-exponential factor (Compensation Effect)                 #
    # ------------------------------------------------------------------ #
    st.header("Step 7 — Pre-exponential Factor via the Compensation Effect")
    st.markdown(
        r"""
        **What:** Obtain the pre-exponential factor A(α) — the second element of the kinetic triplet.

        **Why:** The five isoconversional methods give E(α), but they do not give A(α). The
        compensation effect provides a way to extract A from E without assuming a reaction model.

        **How:** On the Tool page, select the heating rate column to use as the reference experiment
        and click **Compute Compensation Effect**. The tool fits all candidate reaction models to
        that experiment, collects (E, ln A) pairs, and performs a linear regression to obtain the
        compensation line. It then evaluates that line at each E(α) value to produce ln A(α).

        > **Check:** Look at the scatter plot. The (E, ln A) pairs from different models should
        > fall on a clear straight line. If the scatter is large, the compensation effect is
        > unreliable for this dataset.
        """
    )

    with st.expander("Theory — the compensation effect"):
        st.markdown(
            r"""
            ### The empirical observation

            When a family of solid-state reactions (or candidate models) is fitted to TGA data,
            the resulting (E, ln A) pairs follow a **linear relationship**:

            $$\ln A = a + b \cdot E$$

            This is the **compensation effect** (also called the kinetic compensation effect or
            Meyer-Neldel rule). It means that a higher activation barrier is compensated by a higher
            attempt frequency — E and ln A are correlated.

            ### How pICNIK uses it

            1. Take the experimental dα/dt data for one reference heating rate β
            2. Fit the rate equation `dα/dt = A·exp(−E/RT)·f(α)` with each candidate reaction model
               from the `rxnmodel` library (A2, A3, F1, D1, R2, R3, P2, etc.)
            3. Each model fit yields a pair (Eᵢ, Aᵢ)
            4. Linear regression over all (Eᵢ, ln Aᵢ) pairs gives constants **a** and **b**
            5. Apply the line to the isoconversional E(α) from Step 6:
               $$\ln A(\alpha) = a + b \cdot E(\alpha)$$

            This gives ln A at every conversion value, without ever assuming which model is correct.

            ### Output

            An array `ln_A(α)` of the same length as E(α). The actual pre-exponential factor is
            A(α) = exp(ln_A(α)). Natural log units are used throughout to keep the numbers manageable
            (A can range from 10³ to 10¹⁵ min⁻¹ in typical reactions).
            """
        )

    # ------------------------------------------------------------------ #
    # STEP 8: Reaction model reconstruction                                #
    # ------------------------------------------------------------------ #
    st.header("Step 8 — Reaction Model Reconstruction — g(α)")
    st.markdown(
        r"""
        **What:** Numerically reconstruct the integral reaction model g(α) from the E(α) and A(α)
        arrays obtained in the previous steps.

        **Why:** g(α) is the third element of the kinetic triplet. It describes the reaction mechanism
        and is needed for model-based isothermal predictions (Step 9). Its shape can also be compared
        to known analytical models to identify the reaction mechanism.

        **How:** Click **Reconstruct g(α)** on the Tool page. The reconstructed curve is plotted
        alongside a library of analytical models. Compare the shape:

        | Shape of g(α) | Likely mechanism |
        |--------------|-----------------|
        | Linear (slope ≈ 1) | F1 — first-order |
        | Concave (slow then fast) | Diffusion-controlled (D2, D3) |
        | Convex at start | Nucleation-growth (A2, A3) |
        | S-shaped | Power-law (P2, P3) |
        """
    )

    with st.expander("Theory — g(α) and model-free reconstruction"):
        st.markdown(
            r"""
            ### What g(α) is

            The differential reaction model f(α) describes how the rate depends on conversion.
            The integral form g(α) is its cumulative counterpart:

            $$g(\alpha) = \int_0^\alpha \frac{d\alpha'}{f(\alpha')}$$

            For example, for a first-order reaction f(α) = (1−α), integrating gives g(α) = −ln(1−α).

            ### Why reconstruct it numerically

            In model-based analysis, you would guess f(α) and check whether it fits the data.
            In pICNIK's model-free approach, you already know E(α) and A(α) from the isoconversional
            analysis — so you can reconstruct g(α) **directly from the data** without assuming
            any functional form:

            $$g(\alpha) = \sum_{i} A(\alpha_i) \cdot \int_{t_{\alpha_{i-1}}}^{t_{\alpha_i}} \exp\!\left(-\frac{E(\alpha_i)}{RT(t)}\right) dt$$

            Each term in the sum is A times the time integral J over a small α window. Summing from
            0 to α gives the cumulative g(α) — a numerically reconstructed reaction model that is
            consistent with the isoconversional E(α) and A(α) arrays.

            This reconstructed g(α), together with E(α) and A(α), forms the complete **kinetic
            triplet** and enables predictions under any temperature programme.
            """
        )

    # ------------------------------------------------------------------ #
    # STEP 9: Predictions                                                  #
    # ------------------------------------------------------------------ #
    st.header("Step 9 — Kinetic Predictions")
    st.markdown(
        r"""
        **What:** Use the kinetic triplet to predict reaction behaviour under any temperature programme.

        **Why:** This is the ultimate goal — knowing E, A, and g(α) lets you simulate the process
        at conditions you never tested experimentally.

        **How:** The Tool page offers two prediction modes:

        ### Model-free prediction

        Based on E(α) only. Uses the isoconversional equality principle. Three sub-modes:

        | Mode | Description | Input |
        |------|-------------|-------|
        | **Isothermal** | Predict time to reach each α at a constant temperature | Temperature in K |
        | **Linear heating** | Predict α(T) under a new heating rate β | Heating rate in K/min |
        | **Custom** | Predict under any T(t) function | Python function |

        ### Model-based prediction (isothermal only)

        Uses the full kinetic triplet (E, A, g(α)) via:

        $$t(\alpha) = \frac{g(\alpha)}{A \cdot \exp(-E / R T_0)}$$

        More accurate near the experimental conditions. Requires a valid g(α) from Step 8.

        > **Bounds:** The model-free prediction involves a minimisation at each conversion step.
        > The bounds parameter sets the search window in minutes — set it to the expected order
        > of magnitude of the total process duration.
        """
    )

    with st.expander("Theory — how predictions work"):
        st.markdown(
            r"""
            ### The model-free prediction principle

            The isoconversional principle states that for the correct E_α, the time integral of the
            Arrhenius term must be the same across all experiments that reach conversion α:

            $$J[E_\alpha, T(t)_i] = J[E_\alpha, T(t)_j]$$

            where J is the time integral:

            $$J[E, T(t)] = \int_{t_{\alpha - \Delta\alpha}}^{t_\alpha} \exp\!\left(-\frac{E}{RT(t)}\right) dt$$

            For a **prediction**, you supply a new temperature programme T(t) (isothermal,
            linear ramp, or custom). For each small step from αᵢ to αᵢ₊₁, the code finds the
            time t_{i+1} such that the integral J under the new programme equals the experimental J.
            This is a 1D minimisation solved step by step through the conversion array.

            **Output:** three arrays — predicted α, T(t), and t — a complete conversion-vs-time-vs-temperature
            trajectory at conditions that were never tested.

            ### Isothermal model-based prediction

            For isothermal conditions at T₀, the rate equation simplifies to:

            $$\frac{d\alpha}{dt} = A \cdot \exp\!\left(-\frac{E}{RT_0}\right) \cdot f(\alpha)$$

            Separating variables and integrating:

            $$t(\alpha) = \frac{g(\alpha)}{A \cdot \exp(-E / RT_0)}$$

            This gives the time to reach each α directly, without the step-by-step minimisation.
            It uses mean E and A (averaged over α) and the reconstructed g(α) array.
            """
        )

    # ------------------------------------------------------------------ #
    # STEP 10: Export results                                              #
    # ------------------------------------------------------------------ #
    st.header("Step 10 — Export Results")
    st.markdown(
        """
        **What:** Download all computed results as CSV files.

        **Why:** Results are stored in session state during your browser session but are not
        saved permanently. Export everything you need before closing the tab.

        **How:** Every step in the Tool page has download buttons. Available exports:

        | Export | File | Contents |
        |--------|------|---------|
        | Activation energy | `activation_energy_<method>.csv` | α, E, error |
        | Isoconversion tables | `isoconversion_temperature.csv` etc. | T, t, dα/dt tables |
        | Compensation effect | `compensation_effect_lnA.csv` | α, ln(A), error |
        | Model reconstruction | `reaction_model_g_alpha.csv` | α, g(α) |
        | Model-free prediction | `modelfree_prediction_<mode>.csv` | time, T, α |
        | Model-based prediction | `isothermal_prediction_<T>K.csv` | time, α |
        """
    )

    # ------------------------------------------------------------------ #
    # WHY ALL STEPS ARE NECESSARY                                          #
    # ------------------------------------------------------------------ #
    st.divider()
    st.header("Why All Steps Are Necessary")
    st.markdown(
        """
        Each step is required — skipping any one of them makes the result unreliable or impossible:

        | Step | Why it cannot be skipped |
        |------|--------------------------|
        | Multiple heating rates | Without them the isoconversional principle cannot be applied — E and f(α) cannot be separated from a single curve |
        | Temperature range selection | The TGA curve contains multiple processes; you must isolate the one of interest |
        | Conversion α | Normalises mass loss; allows universal mathematical treatment and comparison between runs |
        | Isoconversion tables | Raw data is not at fixed α values — interpolation extracts the isoconversional points the equations require |
        | 5 activation energy methods | Each has different assumptions; comparing them reveals whether E is constant or variable and gives confidence in the result |
        | Compensation effect | The isoconversional methods give E but not A; the compensation trick extracts A using kinetic consistency |
        | g(α) reconstruction | Needed for model-based isothermal predictions and identifies the reaction mechanism |
        | Predictions | The whole point — knowing E, A, g(α) lets you simulate the process at any temperature |
        """
    )

    # ------------------------------------------------------------------ #
    # FAQ                                                                  #
    # ------------------------------------------------------------------ #
    st.divider()
    st.header("Frequently Asked Questions")

    with st.expander("Why does E depend on α?"):
        st.markdown(
            """
            If E is constant across all α, the reaction is a simple single-step process with one
            energy barrier. If E varies, the reaction has multiple overlapping steps each with its
            own barrier — the observed E is a weighted average that shifts as each step dominates
            at different conversion levels.

            A rising E(α) often indicates competing parallel reactions; a falling E(α) often
            indicates a two-step sequential process.
            """
        )

    with st.expander("Why do OFW, KAS, and Fr sometimes give different results?"):
        st.markdown(
            """
            OFW and KAS use different approximations for the temperature integral (Doyle and
            Coats-Redfern respectively). Friedman uses instantaneous rates, which are more sensitive
            to noise in dα/dt.

            If the differences between methods are small (< 5 kJ/mol), all results are consistent.
            Large differences suggest significant E(α) variation — use aVy in that case, as it
            makes the fewest assumptions and handles variable E most accurately.
            """
        )

    with st.expander("What does it mean if E is not constant?"):
        st.markdown(
            """
            It means the process has multiple kinetic steps occurring at different conversion levels,
            each with its own energy barrier. This is common in real materials: moisture evaporation,
            primary decomposition, and secondary oxidation can all overlap in the same temperature
            window.

            A variable E does not invalidate the analysis — it makes it richer. The isoconversional
            methods still give a valid E(α) curve that captures the changing barriers. aVy is
            specifically designed to handle this case.
            """
        )

    with st.expander("What is the compensation effect, physically?"):
        st.markdown(
            """
            Reactions with a high activation energy tend to also have a high pre-exponential factor —
            they attempt to react more often, but each attempt requires more energy. This correlation
            is observed empirically across families of related reactions and across different candidate
            kinetic models fitted to the same dataset.

            pICNIK uses the compensation effect as a mathematical tool to extract A(α) from the
            E(α) values already computed. It does not require any physical explanation for why the
            correlation holds — only that it holds consistently for the candidate models.
            """
        )

    with st.expander("How many heating rate files do I need?"):
        st.markdown(
            """
            **Minimum:** 2 (the tool accepts this, but statistical quality is poor).

            **Recommended:** 4–5 files spanning a reasonable range, e.g., 5, 10, 15, 20 K/min.
            The range should span at least a factor of 2 between the slowest and fastest rate.

            More heating rates give smaller confidence intervals on E. They should be evenly
            distributed on a log scale if possible (e.g., 5, 10, 20 K/min rather than 18, 19, 20).
            """
        )

    with st.expander("Which activation energy method should I use for a publication?"):
        st.markdown(
            """
            For publication-quality results, use **aVy (Advanced Vyazovkin)**. It makes the fewest
            assumptions, handles variable E(α) correctly, and does not require linear heating.

            Report all five methods in a comparison plot — if they agree, it strengthens the
            credibility of the result. If they disagree significantly, discuss the likely source
            (noise in Fr, integral approximation bias in OFW/KAS, assumption of linear heating in Vy).

            Always report confidence intervals and the number of heating rates used.
            """
        )

    # ------------------------------------------------------------------ #
    # REFERENCE TABLE                                                      #
    # ------------------------------------------------------------------ #
    st.divider()
    st.header("Notation Reference")
    st.markdown(
        """
        | Symbol | Meaning | Typical range |
        |--------|---------|---------------|
        | α | Conversion (dimensionless) | 0 to 1 |
        | β | Heating rate | 2–20 K/min typical |
        | T₀ | Initial temperature | ~300 K |
        | E | Activation energy | 50–300 kJ/mol typical |
        | A | Pre-exponential factor | 10³–10¹⁵ min⁻¹ typical |
        | R | Gas constant | 0.008314 kJ/(mol·K) |
        | f(α) | Differential reaction model | dimensionless |
        | g(α) | Integral reaction model | dimensionless, monotonically increasing |
        | dα/dt | Conversion rate | min⁻¹ |
        | J(E, T(t)) | Time integral of Arrhenius term | units of time |
        | I(E, T) | Temperature integral of Arrhenius term | units of temperature |
        """
    )

    st.success(
        "You are ready to use the **Tool** page for your own analysis. "
        "Follow the steps in order: Extract → Conversion → Isoconversion → "
        "Activation Energy → Compensation Effect → Reconstruction → Predictions."
    )


if __name__ == "__main__":
    main()
