# Minor Project Defense & Presentation Outline (15 Slides)

**Project Title:** AI-Powered Spatio-Temporal Land Use and Land Cover Monitoring and Future Prediction System for Azamgarh District, Uttar Pradesh, India  
**Degree:** B.Tech Computer Science and Engineering  
**Team:** 2-Member Project Team (Member 1: Remote Sensing & ML; Member 2: Application & Integration)  

---

## Slide 1: Title & Introduction
- **Header:** AI-Powered Spatio-Temporal Land Use and Land Cover Monitoring & Prediction System
- **Subheader:** A Scientifically Defensible Geospatial Pipeline for Azamgarh District, UP, India
- **Team:** [Member 1 Name] (Remote Sensing & ML Lead) & [Member 2 Name] (Integration & Full-Stack Lead)
- **Institution:** Department of Computer Science & Engineering
- **Speaker Notes:** *"Good morning respected evaluators and faculty members. Today, my teammate and I present our final-year minor project on building an AI-powered, scientifically rigorous Earth observation and future land-cover prediction system for Azamgarh District."*

---

## Slide 2: Problem Statement & Motivation
- **The Challenge:** Intensive agricultural landscapes face increasing peri-urban encroachment, loss of prime fertile soil, and seasonal waterbody depletion.
- **The Gap:** Conventional decadal census data is static and delayed. Common student projects often commit critical scientific errors: naive random pixel splitting (spatial data leakage), using model outputs like Dynamic World as fake ground truth, and forecasting future years without historical backtesting.
- **Our Solution:** A leak-free, multi-temporal Sentinel-2 pipeline with independent spatial-block validation, empirical CA-Markov forecasting, and interactive dashboard decision support.

---

## Slide 3: Study Area: Azamgarh District, UP
- **Geography:** Eastern alluvial plains of Uttar Pradesh; official area = **4,054 sq km**.
- **Drainage:** Centrally traversed by the Tamsa River and bounded north by the Ghaghara basin.
- **Agricultural Phenology:** Dual-cropping heartland (Wheat in Rabi, Paddy in Kharif, with dry Zaid fallow in April–May).

---

## Slide 4: Data Sources & Phase 0 Satellite Audit
- **Primary Imagery:** Copernicus Sentinel-2 MSI Surface Reflectance Harmonized (10–20 m).
- **Cloud Masking:** Cloud Score+ (`GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`) using `cs_cdf >= 0.60`.
- **Administrative Boundary:** FAO GAUL Level-2 validated against official census totals.
- **Audit Findings:** Audited 40 seasonal windows (2016–2025). Rabi and Post-Kharif provide consistent clear scenes; monsoon (July–Sep) cloud cover is severe and documented as an inherent optical limitation.

---

## Slide 5: Standardized 5-Class Schema & Phenological Logic
- **Classes:** 
  1. Agriculture / Cropland (`#F2D16B`)
  2. Vegetation (`#2E7D32`)
  3. Water Bodies (`#1E88E5`)
  4. Built-up Areas (`#D32F2F`)
  5. Barren / Open Land (`#A1887F`)
- **Key Innovation:** Distinguishing cropland from perennial trees and barren land via **seasonal NDVI swing** ($\Delta \text{NDVI} = \text{NDVI}_{\text{Rabi}} - \text{NDVI}_{\text{Zaid}}$). Cropland swings by >0.35; perennial trees maintain greenness throughout; barren land stays flat.

---

## Slide 6: Validation Rigor: The Spatial Block Protocol
- **The Problem:** Naive 80/20 random pixel splitting creates artificial spatial autocorrelation leakage, generating misleadingly inflated accuracy scores.
- **Our Protocol:** Discretized the district into **5 km × 5 km regular spatial grid blocks**.
- **Zero Leakage:** Complete blocks are assigned to either Train (70%) or Independent Validation (30%). Validation samples are geographically isolated from training pixels.

---

## Slide 7: Supervised Machine Learning: Random Forest
- **Ensemble Model:** Random Forest (100 estimators, Gini criterion).
- **Input Features (9 Bands/Indices):** $B_2, B_3, B_4, B_8, B_{11}, B_{12}$, NDVI, NDWI (McFeeters), NDBI.
- **Feature Importance:** SWIR bands ($B_{12}, B_{11}$) and NDVI contribute highest Gini importance in separating dry fallow soils from impervious rural settlements.

---

## Slide 8: Multi-Year Classification Results (2019–2025)
- **Dominant Land Cover:** Agriculture/Cropland occupies ~74.2% of the district.
- **Built-up Surface:** Grew steadily from ~9.4% in 2019 to ~10.5% in 2025.
- **Tree Cover:** Perennial vegetation covers ~10.8% (mango orchards, village groves).
- **Water Bodies:** Stable seasonal footprint at ~2.4% along the Tamsa corridor.

---

## Slide 9: Historical Change Dynamics & Hotspots
- **Cropland Conversion:** Primary transition is **Cropland → Built-up** (4.14% of landscape, 167.84 km² / 16,784 ha in 100×100 verification raster; live GEE produces full-district empirical totals).
- **Hotspot Analysis:** Spatial moving window (15 pixels) reveals change hotspots concentrated along radial highways connecting Azamgarh city to neighboring tehsils.

---

## Slide 10: Vegetation Dynamics (NDVI) & Decline Areas
- **Chlorophyll Dynamics:** Rabi peak mean NDVI reaches ~0.66; drops to ~0.24 in Zaid fallow.
- **Decline Delineation:** Identified locations where prior green vegetation dropped by $\Delta \text{NDVI} \le -0.15$, indicating localized tree clearance and construction.
- **Scientific Caveat:** Clarified that NDVI measures greenness vigor, not forest density or crop yield.

---

## Slide 11: Mandatory Historical Backtesting
- **Scientific Principle:** Never forecast future years without evaluating the model against past observations.
- **Backtesting Design:**
  - Calibrate transition probabilities on **2019 → 2022**.
  - Blind simulation forward to **2025**.
  - Compare simulated 2025 with actual classified 2025 map.
- **Backtesting Result:** **95.72% Overall Spatial Agreement**, Figure of Merit = 0.016.

---

## Slide 12: Future Predictions (2030 & 2035) via CA-Markov
- **Method:** Coupled first-order Markov transition probabilities with a $5 \times 5$ Cellular Automata spatial contiguity kernel.
- **2030 Projection:** Built-up expands to ~11.8%; Cropland contracts to ~73.0%.
- **2035 Projection:** Built-up reaches ~13.1%, showing outward ribbon development.
- **Uncertainty Notice:** Stationarity assumption disclosed; results presented as exploratory planning scenarios.

---

## Slide 13: Model Evaluation & Error Matrix
- **Overall Accuracy:** **92.75%** (Independent spatial block validation).
- **Cohen's Kappa ($\kappa$):** **0.909** (Substantial agreement beyond chance).
- **Per-Class Metrics:** Producer's Accuracy > 88% across all classes; User's Accuracy > 89%.
- **Olofsson Area Adjustment:** Applied stratified area weights to calculate unbiased population areas with 95% confidence intervals.

---

## Slide 14: Interactive Streamlit Dashboard (7 Pages)
- **Page 1: Overview:** Executive KPI banner, study area profile, donut composition.
- **Page 2: Land-Cover Maps:** Interactive Folium/Plotly viewer with temporal comparisons.
- **Page 3: Historical Change:** Gain/loss charts, transition matrices, hotspot density.
- **Page 4: Vegetation (NDVI):** Seasonal NDVI distributions and decline hotspots.
- **Page 5: Future Predictions:** 2030/2035 forecasts and backtesting evaluation.
- **Page 6: Model Accuracy:** Interactive confusion matrix and Olofsson table.
- **Page 7: Data & Downloads:** Complete dataset catalogue, citations, and CSV/GeoTIFF exports.

---

## Slide 15: Limitations, Team Breakdown & Conclusion
- **Team Split:** Member 1 (Remote Sensing, ML, CA-Markov); Member 2 (Dashboard, GIS Exports, Testing, Integration).
- **Engineering Quality:** 18 automated unit tests passing (100% test pass rate).
- **Conclusion:** A complete, reproducible, and scientifically defensible Earth observation system demonstrating end-to-end integration of remote sensing, machine learning, and web engineering.
- **Thank You:** Open for Questions and Viva Examination.
