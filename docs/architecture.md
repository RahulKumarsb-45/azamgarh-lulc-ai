# System Architecture & Pipeline Workflow

This document illustrates the software engineering architecture and the scientific data flow for the **Azamgarh District LULC Monitoring and Future Prediction System**.

---

## 1. System Architecture Diagram

```mermaid
graph TD
    subgraph Data Sources ["Satellite & Vector Inputs"]
        S2["Copernicus Sentinel-2 SR (10-20m)"]
        CS["Cloud Score+ (cs_cdf >= 0.6)"]
        GAUL["FAO GAUL District Boundary (Azamgarh)"]
        DW["Dynamic World V1 (Stratification Guide)"]
    end

    subgraph Preprocessing ["Data Preprocessing & Features"]
        INIT["gee_init.py (OAuth & Project ID)"]
        AUDIT["data_audit.py (40 Seasonal Windows)"]
        INDICES["indices.py (NDVI, NDWI, NDBI, Swing)"]
        SAMPLES["sample_manager.py (5km Spatial Blocks)"]
    end

    subgraph Modeling ["Machine Learning & Forecasting"]
        RF["Random Forest Supervised Classifier"]
        VAL["validation.py (Confusion Matrix & Olofsson Area-Adj)"]
        MARKOV["prediction.py (Markov Transition Matrix)"]
        CAMARKOV["prediction.py (Cellular Automata Simulation)"]
        BACKTEST["prediction.py (Historical Backtesting 2019->2022 to 2025)"]
    end

    subgraph Analysis ["Spatial Analytics"]
        AREAS["area_stats.py (km² and % Share)"]
        CHANGE["change_detection.py (Gains, Losses, Transitions)"]
        VEG["vegetation.py (NDVI Trends & Decline Hotspots)"]
    end

    subgraph Presentation ["Interactive Dashboard (Streamlit)"]
        APP["dashboard/app.py"]
        P1["Page 1: Executive Overview"]
        P2["Page 2: Interactive Land-Cover Maps"]
        P3["Page 3: Historical Change & Hotspots"]
        P4["Page 4: Vegetation & NDVI Dynamics"]
        P5["Page 5: Future Projections (2030, 2035)"]
        P6["Page 6: Model Accuracy & Error Matrix"]
        P7["Page 7: Dataset Catalogue & Downloads"]
    end

    S2 --> CS
    CS --> INDICES
    GAUL --> AUDIT
    AUDIT --> SAMPLES
    SAMPLES --> RF
    INDICES --> RF
    RF --> VAL
    RF --> AREAS
    AREAS --> CHANGE
    CHANGE --> MARKOV
    MARKOV --> CAMARKOV
    CAMARKOV --> BACKTEST
    INDICES --> VEG
    
    AREAS --> APP
    CHANGE --> APP
    VEG --> APP
    CAMARKOV --> APP
    VAL --> APP
    BACKTEST --> APP

    APP --> P1
    APP --> P2
    APP --> P3
    APP --> P4
    APP --> P5
    APP --> P6
    APP --> P7
```

---

## 2. Scientific Data Flow & Validation Pipeline

```mermaid
sequenceDiagram
    autonumber
    participant EE as Google Earth Engine
    participant SM as Spatial Block Manager
    participant ML as Random Forest Classifier
    participant EV as Independent Validation
    participant PR as CA-Markov Predictor
    participant DB as Streamlit Dashboard

    Note over EE,SM: Data Acquisition & Preprocessing
    EE->>EE: Filter Sentinel-2 MSI SR over Azamgarh Boundary
    EE->>EE: Apply Cloud Score+ Mask (cs_cdf >= 0.6)
    EE->>SM: Extract Reflectance & Seasonal Composites
    SM->>SM: Partition into 5 km × 5 km Spatial Blocks
    SM->>SM: Split into Disjoint Train (70%) and Val (30%) Blocks

    Note over ML,EV: Model Training & Evaluation
    SM->>ML: Pass Training Blocks (Zero-Leakage)
    ML->>ML: Fit 100 Trees (Gini Criterion, SWIR + Indices)
    ML->>EV: Predict on Independent Validation Blocks
    EV->>EV: Compute Confusion Matrix, OA, PA, UA, F1, Kappa
    EV->>EV: Apply Olofsson (2014) Area-Adjusted Weights & CIs

    Note over PR,DB: Future Forecasting & Dashboard Rendering
    ML->>PR: Supply Historical Classified Series (2019, 2022, 2025)
    PR->>PR: Calibrate Transition Probability Matrix
    PR->>PR: Run Historical Backtest (Evaluate FoM on 2025)
    PR->>PR: Simulate 2030 & 2035 Landscapes via CA-Markov
    PR->>DB: Deliver Raster Maps, GeoTIFFs, Statistics & Plots
    DB->>DB: Render 7-Page Multi-Dimensional Interactive Interface
```
