"""
Patch the Spanish .po file with missing translations for the refactored
home.py and walkthrough.py views.
Run once, then compile with: pybabel compile -d locales -l es
"""

import re
from pathlib import Path

PO_FILE = Path("locales/es/LC_MESSAGES/messages.po")

# ------------------------------------------------------------
# Mapping: exact msgid → Spanish translation
# ------------------------------------------------------------
TRANSLATIONS = {

    # ---- home.py ------------------------------------------------

    (
        "A web interface for [**pICNIK**](https://pypi.org/project/picnik/), an "
        "open-source Python library for isoconversional kinetic analysis of "
        "thermogravimetric (TGA) data.\n"
        "\n"
        "Upload your TGA files, run the analysis step by step, and download the "
        "results — no Python required."
    ): (
        "Interfaz web para [**pICNIK**](https://pypi.org/project/picnik/), "
        "una biblioteca de Python de código abierto para el análisis cinético "
        "isoconversional de datos termogravimétricos (TGA).\n"
        "\n"
        "Carga tus archivos TGA, ejecuta el análisis paso a paso y descarga los "
        "resultados — sin necesidad de saber Python."
    ),

    "What you can do": "Qué puedes hacer",

    (
        "- Compute the **activation energy E(α)** using five established methods "
        "(Friedman, OFW, KAS, Vyazovkin, Advanced Vyazovkin)\n"
        "- Obtain the **pre-exponential factor A(α)** via the compensation effect\n"
        "- Reconstruct the **reaction model g(α)** from your data\n"
        "- Generate **isothermal and non-isothermal predictions** for any "
        "temperature programme\n"
        "- Export all results as **CSV files** and publication-ready **PNG plots**"
        "\n"
        "- Switch the interface between **Spanish and English**"
    ): (
        "- Calcular la **energía de activación E(α)** con cinco métodos establecidos "
        "(Friedman, OFW, KAS, Vyazovkin, Vyazovkin avanzado)\n"
        "- Obtener el **factor preexponencial A(α)** mediante el efecto de compensación\n"
        "- Reconstruir el **modelo de reacción g(α)** a partir de tus datos\n"
        "- Generar **predicciones isotérmicas y no isotérmicas** para cualquier "
        "programa de temperatura\n"
        "- Exportar todos los resultados como **archivos CSV** y **gráficas PNG** "
        "listas para publicación\n"
        "- Cambiar la interfaz entre **español e inglés**"
    ),

    "The kinetic triplet": "La tripleta cinética",

    (
        "Every pICNIK analysis produces three parameters that together fully "
        "describe the reaction kinetics. Once you have them, you can predict how "
        "much of the material will have reacted at any temperature and time."
    ): (
        "Todo análisis de pICNIK produce tres parámetros que juntos describen "
        "completamente la cinética de reacción. Con ellos puedes predecir cuánto "
        "del material habrá reaccionado a cualquier temperatura y tiempo."
    ),

    (
        "<div style=\"border-left: 4px solid #1f77b4; padding-left: 12px; margin-"
        "bottom: 8px\">\n"
        "\n"
        "**E(α) — Activation energy**\n"
        "\n"
        "The energy barrier the reaction must overcome at each conversion level. "
        "Units: kJ/mol. A constant E means a simple single-step process; a varying"
        " E indicates overlapping steps.\n"
        "\n"
        "            </div>"
    ): (
        "<div style=\"border-left: 4px solid #1f77b4; padding-left: 12px; margin-"
        "bottom: 8px\">\n"
        "\n"
        "**E(α) — Energía de activación**\n"
        "\n"
        "La barrera energética que la reacción debe superar en cada nivel de "
        "conversión. Unidades: kJ/mol. Una E constante indica un proceso simple de "
        "un solo paso; una E variable indica pasos superpuestos.\n"
        "\n"
        "            </div>"
    ),

    (
        "<div style=\"border-left: 4px solid #ff7f0e; padding-left: 12px; margin-"
        "bottom: 8px\">\n"
        "\n"
        "**A(α) — Pre-exponential factor**\n"
        "\n"
        "How frequently molecules attempt to overcome the barrier, per minute. "
        "Obtained from E(α) via the compensation effect — no reaction model "
        "assumed.\n"
        "\n"
        "            </div>"
    ): (
        "<div style=\"border-left: 4px solid #ff7f0e; padding-left: 12px; margin-"
        "bottom: 8px\">\n"
        "\n"
        "**A(α) — Factor preexponencial**\n"
        "\n"
        "Con qué frecuencia intentan superar la barrera las moléculas, por minuto. "
        "Se obtiene de E(α) mediante el efecto de compensación — sin asumir "
        "ningún modelo de reacción.\n"
        "\n"
        "            </div>"
    ),

    (
        "<div style=\"border-left: 4px solid #2ca02c; padding-left: 12px; margin-"
        "bottom: 8px\">\n"
        "\n"
        "**g(α) — Reaction model**\n"
        "\n"
        "Describes how the conversion rate depends on how much has already "
        "reacted. Reconstructed numerically from your data — no model assumed "
        "beforehand.\n"
        "\n"
        "            </div>"
    ): (
        "<div style=\"border-left: 4px solid #2ca02c; padding-left: 12px; margin-"
        "bottom: 8px\">\n"
        "\n"
        "**g(α) — Modelo de reacción**\n"
        "\n"
        "Describe cómo depende la tasa de conversión de cuánto ya ha reaccionado. "
        "Se reconstruye numéricamente a partir de tus datos — sin asumir ningún "
        "modelo previamente.\n"
        "\n"
        "            </div>"
    ),

    "What the tool needs": "Qué necesita la herramienta",

    (
        "pICNIK requires **multiple TGA experiments run at different heating "
        "rates** (at least 2, ideally 4–5). Each experiment is one CSV file with "
        "three columns: time, temperature, and mass.\n"
        "\n"
        "Comparing the same conversion level across experiments at different "
        "heating rates is what allows the tool to extract E(α) without ever "
        "assuming which reaction model applies."
    ): (
        "pICNIK requiere **múltiples experimentos TGA a distintas tasas de "
        "calentamiento** (mínimo 2, idealmente 4–5). Cada experimento es un "
        "archivo CSV con tres columnas: tiempo, temperatura y masa.\n"
        "\n"
        "Comparar el mismo nivel de conversión entre experimentos a distintas tasas "
        "de calentamiento es lo que permite extraer E(α) sin asumir nunca qué "
        "modelo de reacción aplica."
    ),

    (
        "New to isoconversional analysis? Start here. The Tutorial walks you "
        "through all 10 steps with instructions on what to do and what to expect."
    ): (
        "¿Nuevo en el análisis isoconversional? Empieza aquí. El Tutorial te guía "
        "por los 8 pasos con instrucciones sobre qué hacer y qué esperar ver."
    ),

    "Why isoconversion works": "Por qué funciona la isoconversión",

    (
        "The isoconversional principle states that at a fixed conversion level α, "
        "the reaction rate depends only on temperature — not on the reaction "
        "model. Comparing the same α across experiments run at different heating "
        "rates isolates that temperature dependence, which is exactly what Step 6 "
        "does before computing E(α) in Step 7.\n"
        "\n"
        "This is why these methods are called \"model-free\": they don't skip the "
        "reaction model, they just avoid having to guess it before calculating the "
        "activation energy."
    ): (
        "El principio isoconversional establece que, a un nivel de conversión α "
        "fijo, la tasa de reacción depende únicamente de la temperatura — no del "
        "modelo de reacción. Comparar el mismo α entre experimentos realizados a "
        "distintas tasas de calentamiento aísla esa dependencia con la "
        "temperatura, que es justamente lo que hace el Paso 6 antes de calcular "
        "E(α) en el Paso 7.\n"
        "\n"
        "Por eso a estos métodos se les llama \"sin modelo\": no omiten el modelo "
        "de reacción, solo evitan tener que suponerlo antes de calcular la "
        "energía de activación."
    ),

    # ---- walkthrough.py -----------------------------------------

    (
        "This tutorial shows you how to use the **Tool** page step by step. Each "
        "section explains what to do and shows a screenshot of the expected "
        "result. When you are ready, open the **Tool** page from the sidebar."
    ): (
        "Este tutorial muestra cómo usar la página **Herramienta** paso a paso. "
        "Cada sección explica qué hacer y muestra una captura de pantalla del "
        "resultado esperado. Cuando estés listo, abre la página **Herramienta** "
        "desde la barra lateral."
    ),

    "Step 1 — Load Files": "Paso 1 — Cargar archivos",

    (
        "On the Tool page, choose a built-in dataset from the **Choose default "
        "folder** dropdown, or select **Upload files** to load your own CSV files."
        "\n"
        "\n"
        "Each CSV must have **3 columns in order**: time (min) · temperature (°C) "
        "· mass (mg or %).\n"
        "\n"
        "You need at least 2 files — one per heating rate. The tool validates the "
        "structure automatically and confirms how many valid files were loaded."
    ): (
        "En la página Herramienta, elige un dataset integrado del menú "
        "**Seleccionar carpeta predeterminada**, o selecciona **Subir archivos** "
        "para cargar tus propios archivos CSV.\n"
        "\n"
        "Cada CSV debe tener **3 columnas en orden**: tiempo (min) · temperatura (°C) "
        "· masa (mg o %).\n"
        "\n"
        "Necesitas al menos 2 archivos — uno por tasa de calentamiento. La "
        "herramienta valida la estructura automáticamente y confirma cuántos "
        "archivos válidos se cargaron."
    ),

    "Step 1 — Dataset selected and files validated":
        "Paso 1 — Dataset seleccionado y archivos validados",

    "Step 2 — Extract and Visualise Data": "Paso 2 — Extraer y visualizar datos",

    (
        "Click **Extract Data**. The tool reads all files and generates "
        "interactive plots:\n"
        "\n"
        "- **TG (temperature vs mass %)** — shows where the reaction happens; each"
        " file produces one sigmoidal curve\n"
        "- **DTG (temperature vs mass loss rate)** — the peak marks the most "
        "active zone\n"
        "- **dT/dt** — confirms the heating rate is near-constant\n"
        "\n"
        "Curves from higher heating rates appear shifted to higher temperatures. "
        "Use the DTG peak to choose the temperature range in the next step."
    ): (
        "Haz clic en **Extraer datos**. La herramienta lee todos los archivos y "
        "genera gráficas interactivas:\n"
        "\n"
        "- **TG (temperatura vs masa %)** — muestra dónde ocurre la reacción; "
        "cada archivo produce una curva sigmoidal\n"
        "- **DTG (temperatura vs tasa de pérdida de masa)** — el pico marca la "
        "zona de mayor actividad\n"
        "- **dT/dt** — confirma que la tasa de calentamiento es casi constante\n"
        "\n"
        "Las curvas de tasas de calentamiento mayores aparecen desplazadas a "
        "temperaturas más altas. Usa el pico DTG para elegir el rango de "
        "temperatura en el siguiente paso."
    ),

    "Step 2 — TG and DTG plots after extraction":
        "Paso 2 — Gráficas TG y DTG tras la extracción",

    "Step 3 — Conversion": "Paso 3 — Conversión",

    (
        "Use the DTG plot to find where the reaction begins and ends. Set the "
        "**temperature range slider** to those limits, then click **Run "
        "Conversion**.\n"
        "\n"
        "The tool converts the raw mass data into **α (conversion)**: 0 = reaction"
        " not started, 1 = reaction complete. One α(T) curve per file appears on a"
        " shared 0–1 scale."
    ): (
        "Usa la gráfica DTG para encontrar dónde comienza y termina la reacción. "
        "Ajusta el **deslizador de rango de temperatura** a esos límites y haz "
        "clic en **Ejecutar conversión**.\n"
        "\n"
        "La herramienta convierte los datos de masa cruda en **α (conversión)**: "
        "0 = reacción no iniciada, 1 = reacción completa. Aparece una curva α(T) "
        "por archivo en una escala compartida de 0 a 1."
    ),

    "Step 3 — Conversion α(T) curves for all heating rates":
        "Paso 3 — Curvas de conversión α(T) para todas las tasas de calentamiento",

    "Step 4 — Isoconversional Tables": "Paso 4 — Tablas isoconversionales",

    (
        "Leave `d_a = 0.02` (default) and click **Run Isoconversion**.\n"
        "\n"
        "The tool builds three tables: for each conversion level α and each file, "
        "it records the temperature T, time t, and conversion rate dα/dt. One row "
        "per α level, one column per file. These tables are the input to all five "
        "activation energy methods."
    ): (
        "Deja `d_a = 0.02` (predeterminado) y haz clic en **Ejecutar "
        "isoconversión**.\n"
        "\n"
        "La herramienta construye tres tablas: para cada nivel de conversión α y "
        "cada archivo, registra la temperatura T, el tiempo t y la tasa de "
        "conversión dα/dt. Una fila por nivel de α, una columna por archivo. Estas "
        "tablas son la entrada para los cinco métodos de energía de activación."
    ),

    "Step 4 — Isoconversion temperature table (partial view)":
        "Paso 4 — Tabla de temperatura isoconversional (vista parcial)",

    "Step 5 — Activation Energy": "Paso 5 — Energía de activación",

    (
        "Check one or more methods in the list and click **Calculate Activation "
        "Energy**.\n"
        "\n"
        "The tool computes E(α) — how the activation energy changes across the "
        "reaction — and plots it with error bars.\n"
        "\n"
        "- A **flat** curve → simple single-step reaction\n"
        "- A **varying** curve → multiple overlapping steps\n"
        "\n"
        "Start with **KAS** if unsure. Use **aVy** for publications (note: aVy is "
        "slower — allow extra time)."
    ): (
        "Marca uno o más métodos de la lista y haz clic en **Calcular energía de "
        "activación**.\n"
        "\n"
        "La herramienta calcula E(α) — cómo cambia la energía de activación a lo "
        "largo de la reacción — y la grafica con barras de error.\n"
        "\n"
        "- Curva **plana** → reacción simple de un solo paso\n"
        "- Curva **variable** → múltiples pasos superpuestos\n"
        "\n"
        "Empieza con **KAS** si no sabes cuál elegir. Usa **aVy** para "
        "publicaciones (nota: aVy es más lento — dale tiempo extra)."
    ),

    "Step 5 — E(α) curve computed with KAS and OFW methods":
        "Paso 5 — Curva E(α) calculada con los métodos KAS y OFW",

    "Step 6 — Pre-exponential Factor": "Paso 6 — Factor preexponencial",

    (
        "Select the **reference heating rate** (any file works) and click "
        "**Calculate Compensation Effect**.\n"
        "\n"
        "The tool fits candidate reaction models to that file and uses the linear "
        "relationship between E and ln A to compute A(α) at every conversion "
        "level. The results show the compensation line equation and the ln A(α) "
        "curve."
    ): (
        "Selecciona la **tasa de calentamiento de referencia** (cualquier archivo "
        "sirve) y haz clic en **Calcular efecto de compensación**.\n"
        "\n"
        "La herramienta ajusta modelos de reacción candidatos a ese archivo y usa "
        "la relación lineal entre E y ln A para calcular A(α) en cada nivel de "
        "conversión. Los resultados muestran la ecuación de la línea de "
        "compensación y la curva ln A(α)."
    ),

    "Step 6 — Compensation effect results and ln A(α)":
        "Paso 6 — Resultados del efecto de compensación y ln A(α)",

    "Step 7 — Reaction Model Reconstruction":
        "Paso 7 — Reconstrucción del modelo de reacción",

    (
        "Click **Reconstruct g(α)**.\n"
        "\n"
        "The tool numerically reconstructs the integral reaction model g(α) from "
        "your data — no model assumed beforehand. The curve is plotted so you can "
        "compare its shape to known models and identify the likely reaction "
        "mechanism."
    ): (
        "Haz clic en **Reconstruir g(α)**.\n"
        "\n"
        "La herramienta reconstruye numéricamente el modelo de reacción integral "
        "g(α) a partir de tus datos — sin asumir ningún modelo previamente. La "
        "curva se grafica para que puedas comparar su forma con modelos conocidos "
        "e identificar el mecanismo de reacción más probable."
    ),

    "Step 7 — Reconstructed g(α) curve":
        "Paso 7 — Curva g(α) reconstruida",

    "Step 8 — Kinetic Predictions": "Paso 8 — Predicciones cinéticas",

    (
        "The kinetic triplet is now complete (E, A, g(α)). Choose a prediction "
        "mode and click the corresponding **Run** button:\n"
        "\n"
        "- **Model-free isothermal** — enter a temperature (K) → time to reach "
        "each α\n"
        "- **Model-free linear heating** — enter a heating rate (K/min) → α(T) "
        "curve\n"
        "- **Model-based isothermal** — enter a temperature (K) → time using the "
        "full triplet\n"
        "\n"
        "Each prediction produces a downloadable CSV and an interactive plot."
    ): (
        "La tripleta cinética está completa (E, A, g(α)). Elige un modo de "
        "predicción y haz clic en el botón **Ejecutar** correspondiente:\n"
        "\n"
        "- **Isotérmica sin modelo** — ingresa una temperatura (K) → tiempo para "
        "alcanzar cada α\n"
        "- **Calentamiento lineal sin modelo** — ingresa una tasa de calentamiento "
        "(K/min) → curva α(T)\n"
        "- **Isotérmica con modelo** — ingresa una temperatura (K) → tiempo usando "
        "la tripleta completa\n"
        "\n"
        "Cada predicción produce un CSV descargable y una gráfica interactiva."
    ),

    "Step 8 — Isothermal prediction result":
        "Paso 8 — Resultado de predicción isotérmica",

    (
        "You have seen all 8 steps. Open the **Tool** page from the sidebar to run"
        " the analysis with your own data. Download your results with the buttons "
        "next to each table or plot."
    ): (
        "Has visto los 8 pasos. Abre la página **Herramienta** desde la barra "
        "lateral para ejecutar el análisis con tus propios datos. Descarga los "
        "resultados con los botones junto a cada tabla o gráfica."
    ),

    # ---- walkthrough.py — Step 6, updated with the "why" paragraph ----

    (
        "Isoconversion means comparing your experiments at the same conversion "
        "level α instead of the same time or temperature. At fixed α, the reaction "
        "rate depends only on temperature — the reaction model cancels out. That "
        "is what makes it possible to calculate E(α) in the next step without "
        "assuming any reaction model.\n"
        "\n"
        "Leave the **Conversion step size (Δα)** at the default `0.02` and click "
        "**Run Isoconversion**.\n"
        "\n"
        "The tool builds three tables — Temperature (K), Time (min), and Conversion "
        "Rate (Δα/Δt) — one row per α level, one column per heating rate. These "
        "tables are the numerical input to all five activation energy methods.\n"
        "\n"
        "Download any table as CSV with the button below it."
    ): (
        "La isoconversión consiste en comparar tus experimentos al mismo nivel de "
        "conversión α, en lugar de al mismo tiempo o temperatura. A α fijo, la "
        "tasa de reacción depende únicamente de la temperatura — el modelo de "
        "reacción se cancela. Eso es lo que permite calcular E(α) en el siguiente "
        "paso sin asumir ningún modelo de reacción.\n"
        "\n"
        "Deja el **tamaño de paso de conversión (Δα)** en el valor predeterminado "
        "`0.02` y haz clic en **Run Isoconversion**.\n"
        "\n"
        "La herramienta construye tres tablas — Temperatura (K), Tiempo (min) y "
        "Tasa de conversión (Δα/Δt) — una fila por nivel de α, una columna por "
        "tasa de calentamiento. Estas tablas son la entrada numérica para los "
        "cinco métodos de energía de activación.\n"
        "\n"
        "Descarga cualquier tabla como CSV con el botón que aparece debajo."
    ),

    # ---- kinetics/ActivationEnergyControls.py ------------------

    # AE_METHODS values, translated dynamically at usage sites — see the
    # pybabel-extraction shim in ActivationEnergyControls.py.
    "Friedman method": "Método Friedman",
    "Kissinger-Akahira-Sunose method": "Método Kissinger-Akahira-Sunose",
    "Ozawa-Flynn-Wall method": "Método Ozawa-Flynn-Wall",
    "Vyazovkin method": "Método Vyazovkin",
    "Advanced Vyazovkin method": "Método Vyazovkin avanzado",

    "Step 7: Activation Energy Analysis": "Paso 7: Análisis de energía de activación",

    "Complete Step 6 (Isoconversion) first to enable activation energy analysis.":
        "Completa el Paso 6 (Isoconversión) primero para habilitar el análisis de energía de activación.",

    "**Select one or more methods to compute activation energy:**":
        "**Selecciona uno o más métodos para calcular la energía de activación:**",

    "**Search bounds for E (kJ/mol) — Vy / aVy:**":
        "**Límites de búsqueda para E (kJ/mol) — Vy / aVy:**",

    "Lower bound": "Límite inferior",

    "Minimum E value (kJ/mol) the minimizer will consider.":
        "Valor mínimo de E (kJ/mol) que considerará el minimizador.",

    "Upper bound": "Límite superior",

    "Maximum E value (kJ/mol). The true E must fall within [lower, upper].":
        "Valor máximo de E (kJ/mol). El valor real de E debe estar dentro de [límite inferior, límite superior].",

    "Lower bound must be less than upper bound.":
        "El límite inferior debe ser menor que el límite superior.",

    "Confidence level (Advanced Vyazovkin)": "Nivel de confianza (Vyazovkin avanzado)",

    "Confidence level for the error estimation of the Vyazovkin advanced method.":
        "Nivel de confianza para la estimación del error del método Vyazovkin avanzado.",

    "Show error bars": "Mostrar barras de error",

    "Display error bars for the 95-percent confidence interval on the E(α) chart.":
        "Mostrar barras de error del intervalo de confianza del 95 por ciento en la gráfica de E(α).",

    "Calculate Activation Energy": "Calcular energía de activación",

    "Select at least one method before calculating.":
        "Selecciona al menos un método antes de calcular.",

    # ---- kinetics/ActivationEnergyHandler.py -------------------

    "Error creating Activation Energy object: {error}":
        "Error al crear el objeto de energía de activación: {error}",

    "No Activation Energy object available for calculation.":
        "No hay un objeto de energía de activación disponible para el cálculo.",

    "No methods selected.": "No se seleccionaron métodos.",

    "Running {method}...": "Ejecutando {method}...",

    "{method} calculation failed.": "El cálculo de {method} falló.",

    "{method} completed": "{method} completado",

    "Unknown method: {method}": "Método desconocido: {method}",

    "{method} execution failed: {error}": "La ejecución de {method} falló: {error}",

    "Activation Energy Results — E(α)": "Resultados de energía de activación — E(α)",

    "Conversion (α)": "Conversión (α)",

    "E [kJ/mol]": "E [kJ/mol]",

    "Use for downstream steps (Compensation Effect, Reconstruction, Prediction):":
        "Usar en los pasos siguientes (Efecto de compensación, Reconstrucción, Predicción):",

    (
        "The E(α) from this method will be passed to Steps 8–10. aVy is the most "
        "rigorous choice when methods disagree."
    ): (
        "La E(α) de este método se pasará a los Pasos 8–10. aVy es la opción más "
        "rigurosa cuando los métodos no coinciden."
    ),

    "Method details & downloads": "Detalles del método y descargas",

    "Mean E": "E media",
    "Min E": "E mínima",
    "Max E": "E máxima",

    "Download {method} results (CSV)": "Descargar resultados de {method} (CSV)",

    # ---- kinetics/CompensationEffectControls.py ----------------

    "Step 8: Pre-exponential Factor — Compensation Effect":
        "Paso 8: Factor preexponencial — Efecto de compensación",

    "Complete Step 7 (Activation Energy) first to enable this step.":
        "Completa el Paso 7 (Energía de activación) primero para habilitar este paso.",

    "Heating rate data not available.": "Datos de tasa de calentamiento no disponibles.",

    "β = {beta:.2f} K/min (column {i})": "β = {beta:.2f} K/min (columna {i})",

    "Reference heating rate for model fitting":
        "Tasa de calentamiento de referencia para el ajuste de modelos",

    (
        "The compensation effect fits reaction models to data at this heating rate. "
        "The lowest heating rate often gives the best signal."
    ): (
        "El efecto de compensación ajusta modelos de reacción a los datos de esta "
        "tasa de calentamiento. La tasa de calentamiento más baja suele dar la mejor señal."
    ),

    "MSE — Non-Linear fit": "MSE — Ajuste no lineal",
    "R² — Non-Linear fit": "R² — Ajuste no lineal",
    "R² — Linear fit": "R² — Ajuste lineal",

    "Model filter method": "Método de filtrado de modelos",

    (
        "Criterion used to accept or reject each reaction model fit:\n"
        "\n"
        "- **MSE Non-Linear**: keeps fits whose residual sum of squares is below a "
        "threshold (default, robust).\n"
        "- **R² Non-Linear**: keeps fits with a Pearson R² close to 1 from the non-"
        "linear curve fit.\n"
        "- **R² Linear**: linearises the rate equation and keeps fits with high R² "
        "from a linear regression."
    ): (
        "Criterio usado para aceptar o rechazar cada ajuste de modelo de reacción:\n"
        "\n"
        "- **MSE no lineal**: conserva los ajustes cuya suma de residuales al cuadrado "
        "está por debajo de un umbral (predeterminado, robusto).\n"
        "- **R² no lineal**: conserva los ajustes con un R² de Pearson cercano a 1 del "
        "ajuste de curva no lineal.\n"
        "- **R² lineal**: lineariza la ecuación de velocidad y conserva los ajustes con "
        "R² alto de una regresión lineal."
    ),

    "Calculate Compensation Effect": "Calcular efecto de compensación",

    # ---- kinetics/CompensationEffectHandler.py ------------------

    "Activation energy object or results not available.":
        "Objeto o resultados de energía de activación no disponibles.",

    "Computing compensation effect — fitting reaction models to data...":
        "Calculando el efecto de compensación — ajustando modelos de reacción a los datos...",

    (
        "Compensation effect could not be computed. "
        "Try a different reference heating rate column or a different activation energy method."
    ): (
        "No se pudo calcular el efecto de compensación. Prueba con otra columna de "
        "tasa de calentamiento de referencia o con otro método de energía de activación."
    ),

    "Compensation effect computed successfully": "Efecto de compensación calculado con éxito",

    "Error during compensation effect calculation: {error}":
        "Error durante el cálculo del efecto de compensación: {error}",

    "Compensation Effect Results": "Resultados del efecto de compensación",

    "Slope a": "Pendiente a",
    "±{value:.5f} (stderr)": "±{value:.5f} (error estándar)",
    "Intercept b": "Intercepto b",
    "±{value:.4f} (stderr)": "±{value:.4f} (error estándar)",
    "Accepted models": "Modelos aceptados",

    "**Compensation effect equation:** `ln(A) = {a:.4f} · E + {b:.4f}`":
        "**Ecuación del efecto de compensación:** `ln(A) = {a:.4f} · E + {b:.4f}`",

    "Pre-exponential Factor ln(A) vs Conversion α":
        "Factor preexponencial ln(A) vs conversión α",

    "ln(A / min⁻¹)": "ln(A / min⁻¹)",

    "ln(A) statistics": "Estadísticas de ln(A)",

    "**Mean:** {value:.4f}": "**Media:** {value:.4f}",
    "**Min:** {value:.4f}  (α = {alpha:.3f})": "**Mín:** {value:.4f}  (α = {alpha:.3f})",
    "**Max:** {value:.4f}  (α = {alpha:.3f})": "**Máx:** {value:.4f}  (α = {alpha:.3f})",

    "Compensation Effect: ln(A) vs E (by reaction model)":
        "Efecto de compensación: ln(A) vs E (por modelo de reacción)",

    "**Accepted models ({n}):** {names}": "**Modelos aceptados ({n}):** {names}",

    "Download ln(A) Data (CSV)": "Descargar datos de ln(A) (CSV)",

    # ---- kinetics/IsoconversionControls.py ----------------------

    "Step 6: Isoconversion Analysis": "Paso 6: Análisis isoconversional",

    "Complete Step 5 (Conversion) first to enable isoconversion analysis.":
        "Completa el Paso 5 (Conversión) primero para habilitar el análisis isoconversional.",

    "Conversion step size (∆α)": "Tamaño de paso de conversión (∆α)",

    "Step size between conversion values for isoconversion calculations":
        "Tamaño del paso entre valores de conversión para los cálculos isoconversionales",

    "Exact value": "Valor exacto",

    (
        "Type a precise ∆α value — useful for values below 0.01, hard to hit with the "
        "slider."
    ): (
        "Escribe un valor preciso de ∆α — útil para valores menores a 0.01, "
        "difíciles de alcanzar con el deslizador."
    ),

    "Run Isoconversion": "Ejecutar isoconversión",

    # ---- kinetics/IsoconversionHandler.py ------------------------

    "No extracted data available for isoconversion.":
        "No hay datos extraídos disponibles para la isoconversión.",

    "Running isoconversion analysis...": "Ejecutando el análisis isoconversional...",

    "Isoconversion analysis completed": "Análisis isoconversional completado",

    "Error during isoconversion analysis: {error}":
        "Error durante el análisis isoconversional: {error}",

    "Isoconversion Results": "Resultados de isoconversión",

    "Temperature (K)": "Temperatura (K)",
    "Time (min)": "Tiempo (min)",
    "Conversion Rate (∆α/∆t)": "Tasa de conversión (∆α/∆t)",

    "Download Temperature Data (CSV)": "Descargar datos de temperatura (CSV)",
    "Download Time Data (CSV)": "Descargar datos de tiempo (CSV)",
    "Download Conversion Rate Data (CSV)": "Descargar datos de tasa de conversión (CSV)",

    # ---- kinetics/PredictionControls.py --------------------------

    "Step 10: Kinetic Predictions": "Paso 10: Predicciones cinéticas",

    "Complete Step 7 (Activation Energy) first to enable predictions.":
        "Completa el Paso 7 (Energía de activación) primero para habilitar las predicciones.",

    "Model-free Prediction": "Predicción libre de modelo",
    "Model-based Isothermal": "Isotérmica basada en modelo",

    "Temperature program": "Programa de temperatura",
    "Isothermal": "Isotérmico",
    "Linear heating": "Calentamiento lineal",

    (
        "Isothermal: hold at a constant temperature. "
        "Linear heating: ramp at a fixed K/min rate."
    ): (
        "Isotérmico: se mantiene a temperatura constante. "
        "Calentamiento lineal: rampa a una tasa fija en K/min."
    ),

    "Isothermal temperature (K)": "Temperatura isotérmica (K)",
    "Heating rate β (K/min)": "Tasa de calentamiento β (K/min)",
    "Target conversion α": "Conversión objetivo α",

    "Simulation runs until this conversion value is reached.":
        "La simulación corre hasta alcanzar este valor de conversión.",

    "**Time search bounds (min)**": "**Límites de búsqueda de tiempo (min)**",

    (
        "Search window around the previous time point. "
        "Set to the expected order-of-magnitude of the process duration."
    ): (
        "Ventana de búsqueda alrededor del punto de tiempo anterior. Ajusta al orden "
        "de magnitud esperado de la duración del proceso."
    ),

    "Run Model-free Prediction": "Ejecutar predicción libre de modelo",

    (
        "Complete Steps 8 (Compensation Effect) and 9 (Reconstruction) to enable "
        "model-based predictions."
    ): (
        "Completa los Pasos 8 (Efecto de compensación) y 9 (Reconstrucción) para "
        "habilitar las predicciones basadas en modelo."
    ),

    "Constant temperature at which to predict conversion vs time.":
        "Temperatura constante a la que se predice la conversión en función del tiempo.",

    "β = {beta:.2f} K/min": "β = {beta:.2f} K/min",

    "Reference heating rate": "Tasa de calentamiento de referencia",

    "Heating rate whose temperature profile is used for the integral.":
        "Tasa de calentamiento cuyo perfil de temperatura se usa para la integral.",

    "Run Model-based Prediction": "Ejecutar predicción basada en modelo",

    # ---- kinetics/PredictionHandler.py ----------------------------

    "Activation energy object not available.": "Objeto de energía de activación no disponible.",

    "Running {mode} model-free prediction...":
        "Ejecutando la predicción libre de modelo {mode}...",

    "Model-free prediction completed": "Predicción libre de modelo completada",

    "Error during model-free prediction: {error}":
        "Error durante la predicción libre de modelo: {error}",

    (
        "Missing data. Ensure Steps 6 (activation energy), "
        "7 (compensation effect), and 8 (reconstruction) are all complete."
    ): (
        "Faltan datos. Asegúrate de haber completado los Pasos 6 (energía de "
        "activación), 7 (efecto de compensación) y 8 (reconstrucción)."
    ),

    "Running model-based isothermal prediction at T = {iso_T:.0f} K...":
        "Ejecutando la predicción isotérmica basada en modelo a T = {iso_T:.0f} K...",

    "Model-based prediction completed": "Predicción basada en modelo completada",

    "Error during model-based prediction: {error}":
        "Error durante la predicción basada en modelo: {error}",

    "Model-free Prediction — {mode}": "Predicción libre de modelo — {mode}",

    "Predicted Conversion vs Time ({mode})": "Conversión predicha vs tiempo ({mode})",

    "Time [min]": "Tiempo [min]",

    "Final conversion reached": "Conversión final alcanzada",
    "Time to final conversion": "Tiempo hasta la conversión final",

    "Download Prediction Data (CSV)": "Descargar datos de predicción (CSV)",

    "Model-based Isothermal Prediction — T = {iso_T:.0f} K":
        "Predicción isotérmica basada en modelo — T = {iso_T:.0f} K",

    "Model-based Prediction: α vs Time at T = {iso_T:.0f} K":
        "Predicción basada en modelo: α vs tiempo a T = {iso_T:.0f} K",

    "Final conversion": "Conversión final",
    "Total time predicted": "Tiempo total predicho",

    "Download Isothermal Prediction (CSV)": "Descargar predicción isotérmica (CSV)",

    # ---- kinetics/ReconstructionControls.py -----------------------

    "Step 9: Reaction Model Reconstruction — g(α)":
        "Paso 9: Reconstrucción del modelo de reacción — g(α)",

    "Complete Step 8 (Compensation Effect) first to enable reconstruction.":
        "Completa el Paso 8 (Efecto de compensación) primero para habilitar la reconstrucción.",

    "Heating rate for temperature integration":
        "Tasa de calentamiento para la integración de temperatura",

    (
        "The reconstruction integrates exp(-E/RT(t))dt along the temperature "
        "profile of the selected experiment. Using the first (lowest) heating rate "
        "is common."
    ): (
        "La reconstrucción integra exp(-E/RT(t))dt a lo largo del perfil de "
        "temperatura del experimento seleccionado. Es común usar la primera (más "
        "baja) tasa de calentamiento."
    ),

    "Reconstruct g(α)": "Reconstruir g(α)",

    # ---- kinetics/ReconstructionHandler.py -------------------------

    "Missing data. Ensure activation energy and compensation effect have been computed.":
        "Faltan datos. Asegúrate de haber calculado la energía de activación y el efecto de compensación.",

    "Reconstructing g(α)...": "Reconstruyendo g(α)...",

    "Reaction model g(α) reconstructed successfully":
        "Modelo de reacción g(α) reconstruido con éxito",

    (
        "Reconstruction requires accepted_models from the compensation effect step. "
        "Please re-run Step 8 before this step."
    ): (
        "La reconstrucción requiere los modelos aceptados (accepted_models) del paso "
        "de efecto de compensación. Vuelve a ejecutar el Paso 8 antes de este paso."
    ),

    "Error during reconstruction: {error}": "Error durante la reconstrucción: {error}",

    "Reconstructed Integral Model g(α)": "Modelo integral reconstruido g(α)",

    "g(α) reconstructed": "g(α) reconstruido",

    "Reconstructed g(α) vs Accepted Reaction Models":
        "g(α) reconstruido vs modelos de reacción aceptados",

    "Download g(α) Data (CSV)": "Descargar datos de g(α) (CSV)",
}


def normalize(s: str) -> str:
    """Strip and normalize whitespace for comparison."""
    return s.strip()


def patch_po(po_path: Path, translations: dict) -> int:
    content = po_path.read_text(encoding="utf-8")

    patched = 0
    for msgid, msgstr in translations.items():
        # Build the gettext-formatted multiline string for msgid
        # We search for the msgid in the file and replace the empty msgstr
        # Strategy: find the block, check msgstr is empty, replace it.

        # Escape special regex chars in msgid for searching
        # We'll work line by line on the parsed content instead.
        pass

    # Parse the file into blocks
    # Each block: list of lines between blank lines
    lines = content.splitlines(keepends=True)
    result = []
    i = 0

    # Build a lookup: normalized full msgid string → translation
    lookup = {normalize(k): v for k, v in translations.items()}

    while i < len(lines):
        line = lines[i]

        # Detect start of a msgid
        if line.startswith('msgid "') or line.startswith('msgid ""'):
            # Collect the full msgid value
            block_start = i
            msgid_lines = [line]
            i += 1
            while i < len(lines) and (lines[i].startswith('"') or lines[i].strip() == ''):
                if lines[i].strip() == '':
                    break
                msgid_lines.append(lines[i])
                i += 1

            # Parse msgid value
            raw = ''.join(msgid_lines)
            # Extract content between quotes (multiline gettext)
            parts = re.findall(r'"((?:[^"\\]|\\.)*)"', raw)
            msgid_value = ''.join(parts).replace('\\n', '\n').replace('\\"', '"')

            result.extend(msgid_lines)

            # Now look for the msgstr
            # Skip any blank lines between msgid and msgstr
            while i < len(lines) and lines[i].strip() == '':
                result.append(lines[i])
                i += 1

            if i < len(lines) and lines[i].startswith('msgstr'):
                msgstr_line = lines[i]
                msgstr_lines = [msgstr_line]
                i += 1
                while i < len(lines) and lines[i].startswith('"'):
                    msgstr_lines.append(lines[i])
                    i += 1

                # Check if this msgstr is empty
                raw_str = ''.join(msgstr_lines)
                parts_str = re.findall(r'"((?:[^"\\]|\\.)*)"', raw_str)
                msgstr_value = ''.join(parts_str)

                normalized_id = normalize(msgid_value)
                if msgstr_value == '' and normalized_id in lookup:
                    # Replace with translation
                    translation = lookup[normalized_id]
                    new_lines = encode_msgstr(translation)
                    result.extend(new_lines)
                    patched += 1
                    print(f"  Translated: {repr(msgid_value[:60])}")
                else:
                    result.extend(msgstr_lines)
            else:
                pass  # no msgstr found, shouldn't happen
        else:
            result.append(line)
            i += 1

    # Also clear #, fuzzy flags for entries we translated
    final = ''.join(result)

    # Remove fuzzy flags for entries that now have translations
    # (fuzzy = translator should review; we're setting them directly)
    for msgid in translations:
        normalized = normalize(msgid)
        # Simple heuristic: remove #, fuzzy before lines we just translated
        # We'll do a second pass removing orphaned fuzzy flags
    final = re.sub(r'#, fuzzy\n((?:#[^\n]*\n)*)msgid ', r'\1msgid ', final)

    po_path.write_text(final, encoding="utf-8")
    return patched


def encode_msgstr(value: str) -> list[str]:
    """Encode a Python string as gettext msgstr lines."""
    if '\n' not in value:
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return [f'msgstr "{escaped}"\n']

    lines = ['msgstr ""\n']
    for part in value.split('\n'):
        escaped = part.replace('\\', '\\\\').replace('"', '\\"')
        lines.append(f'"{escaped}\\n"\n')
    # Fix: last segment shouldn't have \n if original didn't end with \n
    if not value.endswith('\n'):
        # Replace last \n in the last line: '"...\\n"\n' -> '"..."\n'
        last = lines[-1]
        lines[-1] = last[:-4] + '"\n'  # remove \\n"\n (4 chars) -> add "\n
    return lines


if __name__ == "__main__":
    import os
    os.chdir(Path(__file__).parent)

    print(f"Patching {PO_FILE} ...")
    count = patch_po(PO_FILE, TRANSLATIONS)
    print(f"\nDone — {count} strings translated.")
