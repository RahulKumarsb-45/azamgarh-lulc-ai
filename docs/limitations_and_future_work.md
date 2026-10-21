# Scientific Limitations, Operational Caveats & Future Scope

This document provides a transparent academic disclosure of the constraints, sensor limitations, and prospective technical enhancements for the Azamgarh LULC system.

---

## 1. Remote Sensing & Sensor Limitations

### 1.1 Persistent Monsoon Cloud Cover (July – September)
Optical satellites (Sentinel-2, Landsat) cannot penetrate dense atmospheric clouds. In eastern Uttar Pradesh, the South Asian summer monsoon creates heavy, persistent cloud cover from July through September. 
- **Consequence:** Cloud-free optical observations during the peak Kharif vegetative growth window are scarce.
- **Mitigation:** We focus our primary annual mapping on the **Rabi maturity window (February–March)** and **Post-Monsoon Kharif harvest window (October–November)**, which provide consistent clear-sky acquisitions. Monsoon windows are audited to document this constraint transparently, rather than interpolating unobserved values.

### 1.2 Spatial Resolution & Mixed Pixels (10 m – 20 m)
Sentinel-2 MSI has native spatial resolutions of 10 m (B2, B3, B4, B8) and 20 m (SWIR B11, B12).
- **Consequence:** In densely populated rural landscapes like Azamgarh, small village settlements frequently feature fragmented homesteads, narrow irrigation channels (<5 m width), and dispersed tree clusters smaller than a single 20 m pixel ($400\text{ m}^2$). These "mixed pixels" introduce boundary classification noise between rural settlements and adjacent fields.

---

## 2. Validation & Historical Ground Truth Constraints

### 2.1 Absence of Historical In-Situ Field Surveys
Because this study covers past years (2019 onwards), direct ground-truth GPS field visits for earlier years are physically impossible.
- **Mitigation:** We adhere to the internationally accepted standard of **high-resolution visual interpretation** using dated multi-seasonal Sentinel-2 composites and Google Earth historical high-resolution imagery.
- **Dual-Interpreter Safeguard:** Both team members independently evaluate validation points and track Cohen's kappa agreement to eliminate individual subjective bias. Ambiguous points are excluded rather than guessed.

---

## 3. Future Modeling Assumptions & Uncertainties

### 3.1 The Stationarity Assumption in Markov Chains
First-order Markov transition matrices assume that the transition probabilities observed between historical epochs (2019–2025) will remain constant into 2030 and 2035.
- **Caveat:** In reality, land conversion rates are influenced by non-linear economic shocks, industrial policy changes, new expressway corridors (e.g. Purvanchal Expressway), or regional zoning regulations.
- **Scientific Framing:** Projections must always be cited as **exploratory planning scenarios**, not guaranteed future states.

### 3.2 Backtesting vs. Long-Term Forecasts
While our historical backtesting achieved **95.72% spatial agreement** on 2025, accuracy naturally degrades over longer forecasting horizons (2030, 2035) due to error propagation.

---

## 4. Prospective Future Enhancements

1. **Synthetic Aperture Radar (SAR) Integration:**
   - Incorporating **Sentinel-1 C-band dual-polarization (VV + VH)** SAR backscatter to provide all-weather, cloud-penetrating observations during the cloudy monsoon Kharif season.
2. **Deep Learning Segmentation Models:**
   - Exploring convolutional architectures (e.g. U-Net, DeepLabV3+, or Vision Transformers like SegFormer) to incorporate spatial context and structural textures alongside spectral features.
3. **Multi-Criteria Evaluation (MCE) Suitability Layers:**
   - Integrating vector driver variables (distance to major highways, distance to rivers, distance to urban centers, slope, and population density) into the Cellular Automata spatial allocation engine.
