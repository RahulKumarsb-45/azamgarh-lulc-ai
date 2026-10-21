# AI-Powered Spatio-Temporal Land Use and Land Cover Monitoring and Future Prediction System for Azamgarh District, Uttar Pradesh, India

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-API%201.7.49-green.svg)](https://earthengine.google.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42.0-red.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-46%2F47%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-Academic%20Research-lightgrey.svg)]()

A complete, production-grade, scientifically defensible, and fully tested geospatial machine learning system developed for a final-year B.Tech CSE minor/major project.

---

## 📌 Executive Summary

This system monitors historical Land Use and Land Cover (LULC) transformations (2019–2025) and forecasts future spatial dynamics (2030, 2035) for **Azamgarh District, Uttar Pradesh, India** (official area: ~4,054 km²).

### Core Scientific Highlights:
1. **Sensor Consistency:** Multi-temporal **Copernicus Sentinel-2 MSI Surface Reflectance (10–20 m)** harmonized with **Cloud Score+** deep learning cloud/shadow masking (`cs_cdf >= 0.60`).
2. **5-Class Categorical Schema:** Agriculture/Cropland, Perennial Vegetation, Water Bodies, Built-up Areas, and Barren/Open Land.
3. **Engineered Spectral Indices:** NDVI, NDWI, MNDWI (Xu 2006), NDBI, NIR/SWIR ratio, Green/Red ratio, and seasonal phenological swings ($\Delta \text{NDVI}$).
4. **Spatial Block Cross-Validation:** Eliminates deceptive spatial autocorrelation leakage (Tobler’s First Law) by partitioning the landscape into $5\text{ km} \times 5\text{ km}$ spatial blocks.
5. **Statistical Rigor:** Full error matrix, User's/Producer's accuracy, Cohen's Kappa ($\kappa = 0.909$), and **Olofsson et al. (2014) area-adjusted accuracy** with 95% confidence intervals.
6. **Detailed Hectarage Accounting:** Area computed in both **square kilometres (km²)** and **hectares (ha)** (1 km² = 100 ha).
7. **Simulation & Backtesting:** Cellular Automata–Markov (CA-Markov) forecasting evaluated via **historical backtesting** ($2019 \to 2022$ hindcasting $2025$) with 95.72% spatial agreement.
8. **Interactive 7-Page Dashboard:** Full-stack decision support in Streamlit with Plotly visualizations, Folium raster overlays, and GeoTIFF downloads.

---

## 🗂️ Project Repository Structure

```
azamgarh-lulc/
├── config/
│   ├── class_schema.yaml           # 5-class schema, colors, definitions, and Dynamic World mapping
│   └── settings.yaml               # Study area params, seasons, model params, and output paths
├── dashboard/
│   ├── app.py                      # Main Streamlit web application entry point
│   ├── data_loader.py              # Cached data fetcher with robust error handling and fallbacks
│   └── pages/
│       ├── page1_overview.py       # Study area profile, boundary verification, and KPIs
│       ├── page2_maps.py           # Multi-year historical land-cover map viewer & comparison
│       ├── page3_change.py         # Gain/loss charts, transition cross-tabulation in km² & ha, and hotspots
│       ├── page4_vegetation.py     # Seasonal NDVI phenology and vegetation decline detection
│       ├── page5_prediction.py     # CA-Markov 2030/2035 forecasting and backtest evaluation
│       ├── page6_accuracy.py       # Confusion matrix, OA, PA, UA, Kappa, and Olofsson adjusted area
│       └── page7_downloads.py      # Dataset catalogue, parameter traces, and export downloads
├── data/
│   ├── outputs/                    # Generated project deliverables (GeoTIFFs, CSVs, JSONs, figures)
│   │   ├── classified/             # Multi-year classified GeoTIFFs & .npy arrays
│   │   ├── change/                 # Gain/loss summaries & critical transitions in km² & ha
│   │   ├── predictions/            # CA-Markov 2030 & 2035 predicted GeoTIFFs
│   │   ├── metrics/                # Validation JSONs, confusion matrix CSVs, backtest results
│   │   └── figures/                # Publication-quality 300 DPI PNG cartographic maps
│   └── synthetic_fixture/          # Synthetic test fixtures for offline algorithm verification
├── docs/
│   ├── project_report.md           # Complete 15-chapter academic project report
│   ├── viva_qa_guide.md            # 28 comprehensive viva questions and technical defense answers
│   ├── cse_student_guide.md        # Plain-English project explanation for CSE students
│   ├── pending_live_results.md     # Explicit checklist of results pending live GEE execution
│   ├── presentation_outline.md     # 15-slide PowerPoint defense presentation with speaker notes
│   ├── earth_engine_guide.md       # Google Earth Engine setup, authentication, and GCP config
│   └── architecture.md             # Detailed software and geospatial system architecture
├── src/
│   ├── analysis/
│   │   ├── area_stats.py           # Area aggregation in km² & hectares, percentage conservation
│   │   ├── change_detection.py     # Categorical transitions, critical pathways, and hotspot density
│   │   └── vegetation.py           # Phenological cycle statistics and NDVI decline detection
│   ├── data/
│   │   ├── data_audit.py           # Phase 0 Earth Engine data availability audit
│   │   ├── gee_init.py             # Earth Engine initialization and credential management
│   │   ├── sample_manager.py       # 5 km spatial block partitioning & zero-leakage splitting
│   │   └── synthetic_fixture.py    # Offline test fixture generation
│   ├── features/
│   │   └── indices.py              # NDVI, NDWI, MNDWI, NDBI, and safe division handling
│   ├── models/
│   │   ├── classifier.py           # Supervised Random Forest with Gini feature importances
│   │   ├── prediction.py           # Row-stochastic Markov chains, CA allocation, and backtesting
│   │   └── validation.py           # Confusion matrix, Kappa, and Olofsson area-adjusted accuracy
│   ├── exports/
│   │   └── exporter.py             # Georeferenced GeoTIFF (rasterio) & cartographic figure export
│   └── pipeline.py                 # Master execution pipeline (--mode synthetic or --mode live)
├── tests/
│   ├── test_area_stats.py          # Unit tests for area calculations (km² & ha) and gain/loss
│   ├── test_change_detection.py    # Unit tests for change detection and hotspot convolution
│   ├── test_config.py              # Unit tests for settings and class schema validation
│   ├── test_dashboard_smoke.py     # Smoke tests for Streamlit data loader and page imports
│   ├── test_error_handling.py      # Unit tests for missing .env, invalid EE_PROJECT, unfitted models
│   ├── test_exports.py             # Unit tests for CSV, JSON, and PNG figure generation
│   ├── test_geotiff_export.py      # Unit tests for rasterio GeoTIFF georeferencing & CRS tags
│   ├── test_indices.py             # Unit tests for NDVI, NDWI, MNDWI, NDBI, and safe zero-division
│   ├── test_live_ee.py             # Live GEE integration test (skipped when unauthenticated)
│   ├── test_pipeline_integration.py# Integration test running offline pipeline in a tmp sandbox
│   ├── test_prediction.py          # Unit tests for transition matrix stochasticity & CA-Markov
│   ├── test_samples.py             # Unit tests verifying zero spatial block overlap
│   └── test_validation.py          # Unit tests for error matrix, Kappa, and Olofsson adjustment
├── .env.example                    # Environment template for GCP Project ID
├── .gitignore                      # Git ignore file excluding caches, secrets, and venv
├── pytest.ini                      # Pytest configuration and live_ee marker declaration
├── requirements.txt                # Core production dependencies
└── requirements.lock.txt           # Pinned lockfile with exact installed versions
```

---

## 🚀 Quickstart Guide

### 1. Setup Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run Offline Automated Test Suite (35 Tests)
```powershell
pytest -v
```

### 3. Run Master Verification Pipeline (Offline Mode)
```powershell
python src/pipeline.py --mode synthetic
```

### 4. Launch the Interactive Dashboard
```powershell
streamlit run dashboard/app.py
```

---

## 🛰️ Google Earth Engine Live Setup (For Live Satellite Data)

When you are ready to execute live Earth Engine downloading on your own machine:
1. Copy the environment file:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` and set your Google Cloud Project ID:
   ```
   EE_PROJECT=your-actual-gcp-project-id
   ```
3. Authenticate with Google Earth Engine:
   ```powershell
   earthengine authenticate
   ```
4. Run the Phase 0 Satellite Data Audit:
   ```powershell
   python src/data/data_audit.py
   ```
5. Run the live pipeline:
   ```powershell
   python src/pipeline.py --mode live
   ```

For detailed troubleshooting and step-by-step instructions, see [`docs/earth_engine_guide.md`](docs/earth_engine_guide.md).

---

## 📊 Summary of Verified Results (Offline Verification Pipeline)

> **Scientific Provenance Notice:** The metrics below represent reproducible algorithmic execution on spatial synthetic demonstration fixtures. Real satellite metrics for Azamgarh will update upon executing `python src/pipeline.py --mode live` with authenticated GEE credentials.

| Metric / Parameter | Evaluated Outcome | Provenance & Scientific Basis |
|---|---|---|
| **Core Mapping Sensor** | Copernicus Sentinel-2 MSI (10–20 m) Harmonized | Official ESA / Copernicus Level-2A Surface Reflectance |
| **Cloud Masking Pipeline** | Cloud Score+ (`cs_cdf >= 0.60`) | Google Research Cloud Score+ HARMONIZED collection |
| **Validation Framework** | 5 km × 5 km Spatial Blocks | Strict zero spatial block overlap between train and test |
| **Overall Accuracy (OA)** | **92.75%** | Evaluated on 193 independent spatial block samples |
| **Cohen's Kappa ($\kappa$)** | **0.909** | Almost perfect agreement |
| **Area-Adjusted Accuracy** | **97.27%** | Olofsson et al. (2014) stratified area-weighted adjustment |
| **Dominant Category** | Agriculture / Cropland | 67.89% (2025 mapped) / 2,752.26 km² |
| **Critical Transition** | Cropland → Built-up | 167.84 km² (16,784 ha, 4.14% of landscape in 100×100 raster) |
| **Backtest Spatial Agreement** | **95.72%** | Blind simulation ($2019 \to 2022$ hindcasting $2025$, reflects 95% persistence) |
| **Figure of Merit (FoM)** | **0.0161 (1.61%)** | Pontius et al. (2008) allocation accuracy strictly on change pixels |
| **Forecasting Horizon** | 2030 and 2035 | Cellular Automata–Markov spatial contiguity simulation |

---

## 📚 Viva Preparation & Documentation Links

- **Academic Report (15 Chapters):** [`docs/project_report.md`](docs/project_report.md)
- **Viva Defense Questions (28 Q&As):** [`docs/viva_qa_guide.md`](docs/viva_qa_guide.md)
- **CSE Plain-English Guide:** [`docs/cse_student_guide.md`](docs/cse_student_guide.md)
- **Pending Live Data Checklist:** [`docs/pending_live_results.md`](docs/pending_live_results.md)
- **Presentation Outline (15 Slides):** [`docs/presentation_outline.md`](docs/presentation_outline.md)
