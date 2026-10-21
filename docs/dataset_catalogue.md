# Remote Sensing Dataset Catalogue & Source Documentation

This document catalogs every satellite collection, cloud assessment product, reference model, and administrative boundary dataset used in the Azamgarh LULC monitoring system.

---

## 1. Primary Sensor: Sentinel-2 Multi-Spectral Instrument (MSI)

- **Collection Earth Engine ID:** `COPERNICUS/S2_SR_HARMONIZED`
- **Provider:** European Space Agency (ESA) / Copernicus Programme / Google Earth Engine
- **Processing Level:** Level-2A (Bottom-of-Atmosphere / Surface Reflectance)
- **Harmonization Notice:** The `HARMONIZED` collection applies offset adjustments to harmonize radiometric differences introduced by ESA's baseline processing change in early 2022.
- **Temporal Coverage:** 2017-03-28 to Present (Note: Global systematic L2A processing over India stabilized in 2018–2019; prior acquisitions may be incomplete or TOA only).
- **Spatial Resolution & Spectral Bands:**
  | Band Name | Description | Center Wavelength | Native Resolution | Role in Schema |
  |---|---|---|---|---|
  | **B2** | Blue | 490 nm | 10 m | Soil / water / atmospheric baseline |
  | **B3** | Green | 560 nm | 10 m | Water index (NDWI) numerator |
  | **B4** | Red | 665 nm | 10 m | Chlorophyll absorption, NDVI numerator |
  | **B8** | Broad NIR | 842 nm | 10 m | Cellular scattering, NDVI & NDWI |
  | **B11** | SWIR-1 | 1610 nm | 20 m | Moisture absorption, NDBI numerator |
  | **B12** | SWIR-2 | 2190 nm | 20 m | Impervious / rock / bare soil contrast |
- **Licensing:** Free, full, and open access under the EU Copernicus Programme.

---

## 2. Cloud and Shadow Masking: Cloud Score+ S2_HARMONIZED

- **Collection Earth Engine ID:** `GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`
- **Provider:** Google Research
- **Quality Band:** `cs_cdf` (Cumulative Distribution Function of clear-sky observation quality, range 0.0 to 1.0)
- **Implementation Threshold:** Pixels with `cs_cdf >= 0.60` are classified as clear observations. Lower scores indicate cirrus clouds, thick cumulus clouds, or cloud shadows.
- **Citation:** Pasquarella, V. J., et al. (2023). *Cloud Score+: A global cloud and cloud shadow masking dataset for Sentinel-2.*

---

## 3. Reference Land Cover Product: Dynamic World V1

- **Collection Earth Engine ID:** `GOOGLE/DYNAMICWORLD/V1`
- **Provider:** World Resources Institute (WRI) & Google
- **Spatial Resolution:** 10 m near-real-time deep learning model output
- **Scientific Role in Project:** 
  > **STRICT SCIENTIFIC RULE:** Dynamic World is used **strictly for sample stratification guidance and qualitative comparison**, NEVER as independent ground truth. Claiming accuracy of our classifier using Dynamic World as ground truth would be scientifically invalid because Dynamic World is itself a machine-learning model prediction with known regional misclassification errors in mixed agricultural mosaics.
- **Citation:** Brown, C. F., et al. (2022). *Dynamic World, Near real-time global 10m land use land cover mapping.* Scientific Data, 9(1), 251.

---

## 4. Fallback Sensor: Landsat Collection 2 Level-2

- **Earth Engine IDs:**
  - Landsat 7 ETM+: `LANDSAT/LE07/C02/T1_L2` (1999–2022; SLC-off after 2003)
  - Landsat 8 OLI: `LANDSAT/LC08/C02/T1_L2` (2013–Present)
  - Landsat 9 OLI-2: `LANDSAT/LC09/C02/T1_L2` (2021–Present)
- **Spatial Resolution:** 30 m multispectral
- **Sensor Consistency Rule:** Landsat observations (30 m) are evaluated in the audit as a potential fallback for pre-2018 analysis. If Landsat is used, it is reported as an independent 30 m series and never silently aggregated with 10 m Sentinel-2 change statistics without documented spatial resampling.

---

## 5. Administrative District Boundary

- **Primary Source:** `FAO/GAUL/2015/level2` (Global Administrative Unit Layers)
- **Alternative Source:** `FAO/GAUL/2025/level2`
- **Verification Criterion:**
  - State: `Uttar Pradesh`
  - District: `Azamgarh`
  - GAUL 2015 Computed Area: ~4,228 sq km (geometric geodesic polygon).
  - Official Census of India / UP District Portal Area: **4,054 sq km**.
  - Variance: Documented in methodology. GAUL administrative boundaries carry a standard United Nations disclaimer regarding international and internal boundary delineations. Mapped percentages are scaled to official reference baselines.
