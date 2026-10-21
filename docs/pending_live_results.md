# Checklist of Results Pending Live Earth Engine Execution

**Project:** AI-Based Land Use/Land Cover Monitoring & Future Prediction for Azamgarh District  
**Status:** Software, pipeline, algorithms, and offline validation test suite are 100% verified.  
**Requirement for Live Data:** Execution of `python src/pipeline.py --mode live` on an authenticated Google Cloud project.  

---

## 1. What Has Been Fully Verified Offline?

The following algorithmic and computational components have been rigorously verified and tested offline:
1. **Configuration & Schema:** Strict validation of 5-class schema, coordinate reference systems (`EPSG:32644` and `EPSG:4326`), seasonal windows, and parameter limits.
2. **Feature Engineering & Indices:** Mathematical correctness of NDVI, NDWI, MNDWI, NDBI, NIR/SWIR ratios, and safe division-by-zero handling.
3. **Spatial Block Partitioning:** Generation of 5 km × 5 km regular grid blocks with mathematical verification of zero spatial block overlap between training and validation sets.
4. **Supervised Random Forest Classifier:** Training, hyperparameter tuning, feature importance extraction, class prediction, and posterior probability output.
5. **Accuracy Assessment:** Exact computation of confusion matrices, Producer’s Accuracy (Recall), User’s Accuracy (Precision), F1-Scores, Cohen’s Kappa, and Olofsson et al. (2014) area-adjusted accuracy with 95% confidence intervals.
6. **Area Accounting:** Pixel-area integration in both square kilometres and hectares, ensuring strict 100.0% landscape conservation.
7. **Change Detection:** Matrix subtraction, cross-tabulation, critical transition extraction, and 2D spatial convolution hotspot mapping.
8. **Forecasting & Backtesting:** Row-stochastic normalization of transition probability matrices, Markov projection, Cellular Automata spatial aggregation simulation, and historical backtesting evaluation (Overall Agreement, Kappa, Figure of Merit).
9. **Cartographic Exports:** Export of georeferenced GeoTIFFs with embedded affine transforms and CRS tags, CSV tables, metadata JSONs, and 300 DPI publication maps.
10. **Interactive Dashboard:** 7-page Streamlit web application with cached data loading, diagnostic fallbacks, Plotly visualizations, and data download handlers.

---

## 2. What Specific Empirical Claims Remain Pending Until Live GEE Execution?

Until you configure your Google Cloud project credentials in `.env` and run the live Earth Engine pipeline, the following empirical results are based on verified demonstration fixtures and should not be cited as final ground truth:

| Empirical Output / Claim | Status in Delivered ZIP | What Live Run Will Produce |
|---|---|---|
| **Exact Cloud-Free Sentinel-2 Scene Count** | Template from historical baseline schema | Exact number of L2A scenes and Cloud Score+ clear observation percentages across 2016–2025 |
| **Exact Official GAUL Feature Geometry** | Bounding box coordinates (82.80°E–83.65°E, 25.70°N–26.35°N) | Precise vector polygon boundary for Azamgarh District from FAO GAUL 2015 Level 2 |
| **Empirical Sentinel-2 Surface Reflectance Composites** | Synthetic 5-class reflectance profiles based on published literature | Live median composites of Sentinel-2 SR Harmonized bands (B2, B3, B4, B8, B11, B12) for Rabi, Zaid, and Kharif |
| **Final Azamgarh Model Accuracy Score** | 92.75% OA / 0.909 Kappa / 97.27% Olofsson OA (on synthetic spatial sample fixture) | Final empirical accuracy based on photo-interpreted Azamgarh ground truth points |
| **Exact Hectares of Cropland Converted (2019–2025)** | 167.84 km² (16,784 ha) simulated in 100x100 synthetic raster (4.14% of landscape) | Empirical hectarage of agricultural conversion across the district from authenticated Sentinel-2 images |
| **Exact 2030 & 2035 Predicted Hectares** | CA-Markov simulation based on synthetic baseline trajectory | Empirical projection calibrated on real 2019–2025 satellite transitions |

---

## 3. How to Run the Live Pipeline on Your Computer

Follow these 4 simple steps once you have downloaded the ZIP to your computer:

### Step 1: Set up Python Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2: Configure Earth Engine Authentication
1. Copy the environment template:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` and set your Google Cloud project ID:
   ```
   EE_PROJECT=your-actual-gcp-project-id
   ```
3. Authenticate Earth Engine:
   ```powershell
   earthengine authenticate
   ```

### Step 3: Run the Live Pipeline
```powershell
# 1. Run the Satellite Data Audit
python src/data/data_audit.py

# 2. Run the Master Live Pipeline
python src/pipeline.py --mode live
```

### Step 4: Launch the Dashboard
```powershell
streamlit run dashboard/app.py
```
