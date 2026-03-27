import streamlit as st


def show():
    st.title("pICNIK Web UI", anchor=False)
    st.markdown(
        """
        A web interface for **isoconversional kinetic analysis** of thermogravimetric (TGA) data.

        If you have a solid material — a polymer, mineral, pharmaceutical, or biomass — and you want
        to know how it decomposes when heated, and how fast that process would happen at *any* temperature,
        this is your tool.
        """
    )


def show_description():
    st.subheader("What pICNIK does", anchor=False)
    st.markdown(
        """
        A **TGA experiment** heats a small sample at a controlled rate and continuously records its mass.
        As the material decomposes, gases escape and the mass drops. pICNIK analyses a set of these
        experiments — each run at a **different heating rate** — and extracts the three parameters
        that fully describe the reaction kinetics:
        """
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            **E(α) — Activation energy**
            The energy barrier molecules must overcome to react, at each conversion level.
            Units: kJ/mol.

            The rate depends on E through the exponential term exp(−E/RT) — because E appears
            in the exponent, a higher E makes the rate drop much faster as temperature decreases.
            In practice: a high-E reaction is nearly dormant at low temperatures and then
            accelerates steeply once enough thermal energy is available. The transition from
            "barely reacting" to "reacting fast" happens over a much narrower temperature window
            than for a low-E reaction.
            """
        )
    with col2:
        st.markdown(
            """
            **A(α) — Pre-exponential factor**
            The rate at which molecules in the bulk sample attempt to react, per minute.
            Units: 1/min.

            Each molecule crosses the energy barrier only once — after that it has reacted
            and is gone. But a solid sample contains ~10²³ molecules all attempting
            independently and simultaneously. **A** captures how frequently those attempts
            occur across the whole population. A higher **A** means more attempts per minute,
            so more reactions succeed per unit time even if the barrier stays the same.

            Obtained from E(α) via the compensation effect.
            """
        )
    with col3:
        st.markdown(
            """
            **g(α) — Reaction model**
            A function of the conversion α that describes *why the rate is what it is*
            at each stage of the reaction — not just how much material is left, but the
            physics and geometry of how it reacts.

            Think of it this way: two reactions can both be 50% done (α = 0.5) yet have
            very different rates at that point — one speeding up, the other slowing down.
            **g(α)** captures that difference. It tells you whether the reaction slows
            because less material remains, because the reacting surface is shrinking, or
            because products are blocking the reaction front.

            pICNIK reconstructs **g(α)** numerically from the data, so you never have
            to guess which mechanism applies.
            """
        )

    st.markdown(
        """
        Together these three form the **kinetic triplet**. Once known, you can predict how much of
        the material will have reacted at any temperature and time — whether in an industrial furnace,
        a storage facility, or a laboratory reactor.
        """
    )

    st.divider()
    st.subheader("Why multiple heating rates?", anchor=False)
    st.markdown(
        """
        The **isoconversional principle** is the mathematical foundation of pICNIK. It states that
        at a fixed conversion α, the reaction rate depends *only* on temperature — not on how the
        sample was heated to get there. This means that by comparing the same conversion level
        across experiments run at different heating rates, it is possible to extract the activation
        energy **without ever assuming which reaction model applies**.

        With just one heating rate you cannot separate E from the reaction model. You need at least
        3 experiments, ideally 4–5, spanning a reasonable range (e.g., 5, 10, 15, 20 K/min).
        """
    )

    st.divider()
    st.subheader("The analysis workflow", anchor=False)
    st.markdown(
        """
        ```
        Raw TGA files  (one CSV per heating rate)
                │
                ▼
        1. Read & clean data        →  heating rates β, initial temperatures T₀
                │
                ▼
        2. Compute conversion α     →  α(T) curves, 0 = unreacted · 1 = complete
                │
                ▼
        3. Build isoconversion tables  →  T, t, dα/dt  at fixed α values across all runs
                │
                ▼
        4. Compute activation energy E(α)  →  five methods: Fr, OFW, KAS, Vy, aVy
                │
                ▼
        5. Compensation effect      →  obtain ln A(α) from E(α)
                │
                ▼
        6. Reconstruct reaction model g(α)  →  numerical, no model assumed
                │
                ▼
        7. Predict behavior         →  at any constant or programmed temperature
        ```
        """
    )

    st.divider()
    st.subheader("Five activation energy methods", anchor=False)
    st.markdown(
        """
        pICNIK computes E(α) using five established isoconversional methods, so you can compare
        results and assess their reliability:
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            - **Fr — Friedman**: differential, most sensitive, highest accuracy when data is clean
            - **OFW — Ozawa-Flynn-Wall**: integral, simple, slight approximation bias
            - **KAS — Kissinger-Akahira-Sunose**: integral, better approximation than OFW
            """
        )
    with col2:
        st.markdown(
            """
            - **Vy — Vyazovkin**: numerical optimisation, no approximation, handles variable E well
            - **aVy — Advanced Vyazovkin**: most rigorous, incremental integration, best for complex reactions
            """
        )

    st.info(
        "If all five methods agree, your data is consistent and the result is reliable. "
        "If they diverge, use aVy as the reference — it makes the fewest assumptions."
    )


def show_workflow():
    st.divider()
    st.subheader("Get started", anchor=False)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 1. Tutorial")
        st.write(
            "Step-by-step guide with theory, formulas, and worked examples. "
            "Start here if you are new to isoconversional analysis."
        )
        if st.button("Go to Tutorial", key="home_btn_tutorial"):
            st.switch_page("src/views/walkthrough.py")
    with col2:
        st.markdown("### 2. Tool")
        st.write(
            "Upload your TGA CSV files and run the full analysis: extraction, conversion, "
            "isoconversion, activation energy, compensation effect, reconstruction, and predictions."
        )
        if st.button("Go to Tool", key="home_btn_tool"):
            st.switch_page("src/views/tool.py")
    with col3:
        st.markdown("### 3. Export")
        st.write(
            "Download results as CSV files directly from the Tool page after each step. "
            "Every computed table and curve can be exported."
        )


show()
show_description()
show_workflow()
