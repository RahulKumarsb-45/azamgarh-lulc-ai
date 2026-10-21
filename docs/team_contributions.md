# Two-Member Project Contribution Breakdown

This document outlines the division of engineering and scientific responsibilities between the two team members for academic evaluation and viva defense.

---

## Member 1: Remote Sensing, Machine Learning & Geospatial Modeling

**Primary Role:** Remote Sensing Scientist & Machine Learning Engineer  
**Core Responsibilities:**
1. **Satellite Data Acquisition & Auditing:**
   - Multi-temporal satellite data query design across Sentinel-2 L2A and Landsat collections.
   - Cloud masking workflow design using Google Cloud Score+ (`cs_cdf >= 0.60`).
   - Boundary verification and area calculation against official Azamgarh baselines.
2. **Feature Engineering & Phenology:**
   - Implementation of spectral indices (NDVI, NDWI McFeeters 1996, NDBI).
   - Formulation of seasonal phenological swing metrics ($\Delta \text{NDVI}$) to resolve cropland vs. perennial vegetation ambiguity.
3. **Machine Learning Classification:**
   - Supervised Random Forest model configuration, hyperparameter tuning, and Gini feature importance extraction.
   - Translation of classifier parameters to Earth Engine `ee.Classifier.smileRandomForest`.
4. **Independent Validation & Statistical Protocol:**
   - Implementation of spatial block cross-validation (5 km blocks) to eliminate spatial data leakage.
   - Error matrix generation, Producer's and User's accuracy, F1-Score, and Cohen's Kappa.
   - Implementation of Olofsson et al. (2014) area-adjusted accuracy and standard error formulas.
5. **Predictive Modeling & Backtesting:**
   - First-order discrete-time Markov chain transition probability calculation.
   - Cellular Automata–Markov (CA-Markov) spatial contiguity modeling for 2030 and 2035.
   - Execution and evaluation of mandatory historical backtesting (2019→2022 to 2025).

---

## Member 2: Software Architecture, Full-Stack Dashboard & Integration

**Primary Role:** Full-Stack Dashboard Developer & Integration Engineer  
**Core Responsibilities:**
1. **Software Architecture & Repository Engineering:**
   - Python virtual environment configuration and dependency management (`requirements.txt`, `requirements.lock.txt`).
   - Centralized YAML settings and class schema management (`config/settings.yaml`, `config/class_schema.yaml`).
   - Git hygiene, `.gitignore` rules, and environment variable configuration (`.env.example`).
2. **Interactive Streamlit Dashboard:**
   - Multi-page application architecture (`dashboard/app.py` and 7 sub-pages).
   - CSS styling, custom KPI cards, and responsive layout design.
   - Data caching with `@st.cache_data` and resilient fallback handling.
   - Dynamic data visualization using Plotly (donut charts, gain/loss bars, trend lines, confusion matrix heatmaps).
   - Interactive GIS map visualization with Folium and raster colormaps.
3. **Data Export & Cartographic Products:**
   - Georeferenced GeoTIFF raster export pipeline using `rasterio`.
   - CSV tabular export handlers and JSON metadata serialization.
   - Automated generation of publication-quality static figures (PNG/PDF) with legends, scales, and north arrows.
4. **Testing, Quality Assurance & Verification:**
   - Automated unit test suite development with `pytest` across 6 test modules (18 unit tests).
   - Offline synthetic test fixture generation for reproducible offline execution.
   - Windows PowerShell automation, character encoding fixes, and diagnostic tooling.
5. **Documentation & Deliverables Assembly:**
   - Setup guides, troubleshooting documentation, and minor project report outline.
   - Presentation slides outline and viva voce defense preparation notes.

---

## Joint Responsibilities
- Independent dual-interpreter visual labeling of validation points and resolution of disagreements.
- Joint verification of historical backtesting results and model assumptions.
- Preparation and delivery of the final minor project defense presentation and viva examination.
