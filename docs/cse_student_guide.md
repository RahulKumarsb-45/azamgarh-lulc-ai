# Simple Project Explanation for Computer Science & Engineering Students

**Topic:** AI-Based Land Use/Land Cover (LULC) Classification, Change Detection, and Future Prediction for Azamgarh District, UP, India  
**Target:** CSE Final Year / Minor Project Viva Preparation  

---

## 1. What Problem Are We Solving?

Imagine you are looking at a satellite image of an entire district from space. You want to know:
- How much of the land is farm fields (Cropland)?
- How much is trees/orchards (Vegetation)?
- Where are the rivers and ponds (Water)?
- Where are the houses, shops, and roads (Built-up)?
- Where is bare dirt or wasteland (Barren Land)?
- More importantly: **How has this changed over the last 6 years (2019 to 2025), and what will it look like in 2030 and 2035?**

Traditionally, governments sent survey officers on motorbikes once every 10 years to write reports. That is slow, expensive, and subject to human error. Our software automates this entire process using Satellite Remote Sensing + Machine Learning + Markov Chain modeling.

---

## 2. The Core Technical Pipeline (Step-by-Step for Coders)

```
[Satellite Data: Sentinel-2]
           │
           ▼
[Preprocessing & Cloud Screening: Cloud Score+]
           │
           ▼
[Feature Engineering: Bands + NDVI, NDWI, MNDWI, NDBI]
           │
           ▼
[Spatial Block Split: 5km x 5km blocks -> Train / Test]
           │
           ▼
[ML Model: Random Forest Classifier (100 Trees)]
           │
           ▼
[Validation: Confusion Matrix + Olofsson Area Adjustment]
           │
           ▼
[Change Detection: Matrix Subtraction & Transition Tracking]
           │
           ▼
[Simulation: Cellular Automata - Markov Chain (2030, 2035)]
           │
           ▼
[Decision Support: Interactive Streamlit Dashboard]
```

---

## 3. Key Concepts Explained in CSE Terms

### A. Multispectral Bands = 2D Feature Channels
A normal smartphone camera takes RGB photos (3 color channels: Red, Green, Blue).  
The European Space Agency's **Sentinel-2** satellite has 13 spectral bands. It sees light humans cannot see:
- **Near-Infrared (NIR - Band 8):** Plants reflect NIR like crazy. Healthy plants look blindingly bright in NIR.
- **Short-Wave Infrared (SWIR - Bands 11 & 12):** Water absorbs SWIR completely (appears pitch black), while concrete, asphalt, and dry soil reflect SWIR strongly.

In our code, a satellite image is simply a 3D NumPy array of shape `(Height, Width, Bands)`.

### B. Spectral Indices = Mathematical Feature Transformations
Instead of just feeding raw bands into a model, we engineer domain-specific normalized ratios:
- $\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$: High for green plants ($> 0.6$), low for soil ($0.2$), negative for water ($-0.3$).
- $\text{NDWI} = \frac{\text{Green} - \text{NIR}}{\text{Green} + \text{NIR}}$: High for rivers and ponds ($> 0.2$).
- $\text{MNDWI} = \frac{\text{Green} - \text{SWIR1}}{\text{Green} + \text{SWIR1}}$: Even sharper water detector that doesn't get confused by building shadows.
- $\text{NDBI} = \frac{\text{SWIR1} - \text{NIR}}{\text{SWIR1} + \text{NIR}}$: High for concrete, brick kilns, asphalt, and settlements.

### C. Random Forest Classifier = Ensemble of Decision Trees
We train an ensemble of 100 Decision Trees (`sklearn.ensemble.RandomForestClassifier`). Each tree votes on the class of each pixel. Random Forest is ideal because:
- It handles non-linear relationships.
- It doesn't overfit easily.
- It gives us feature importance (e.g. Band 12 and NDVI are our top predictors).

### D. The "Spatial Autocorrelation" Trap (Very Important for Viva!)
In normal ML (like predicting house prices or spam emails), you do `train_test_split(X, y, test_size=0.3)`.  
**In satellite imagery, doing that is CHEATING!**  
Why? Because pixel $(x, y)$ and pixel $(x+1, y)$ are right next to each other on the ground. If you put one in Train and one in Test, your model isn't learning to classify land cover—it's just memorizing that neighborhood!  
**Our Fix:** We divide the district into $5\text{ km} \times 5\text{ km}$ spatial blocks. If a block is in Train, none of its pixels are allowed in Test. This guarantees true out-of-sample testing.

### E. Markov Chains = Transition Probability Matrix
A Markov Chain models state transitions over time.  
If we observe how pixels changed from 2019 to 2025:
- What is the probability that Cropland turns into Built-up? ($P_{1 \to 4}$)
- What is the probability that Cropland stays Cropland? ($P_{1 \to 1}$)  
We organize these probabilities into a $5 \times 5$ matrix where each row sums to $1.0$. To predict the future:
$$v_{2030} = v_{2025} \times P$$

### F. Cellular Automata (CA) = Neighborhood Rules
A pure Markov chain tells you *how many* hectares will become houses, but not *where*.  
Cellular Automata uses a 2D convolution kernel (Moore neighbourhood) over the map:
- If a farm pixel is surrounded by existing houses and roads, it has a much higher probability of converting into built-up area than a farm pixel 20 km away in the middle of nowhere.
- This creates realistic, organic urban growth rather than random noise pixels.

### G. Historical Backtesting = Hindcasting
Before trusting our 2030 and 2035 predictions, we test the algorithm on the past:
1. Train the transition matrix on $2019 \to 2022$.
2. Simulate $2025$.
3. Compare the simulated 2025 map with the **actual** 2025 satellite map.
4. Calculate Overall Agreement, Kappa, and Figure of Merit (FoM). If the backtest passes, the model is scientifically defensible.

---

## 4. Software Engineering Highlights of this Codebase

- **Modular Architecture:** All algorithms live in `src/` modules; all settings live in `config/settings.yaml`.
- **Offline & Online Separation:** The software runs completely offline with verified mathematical test fixtures, and switches to live satellite downloading via Earth Engine with a single flag (`--mode live`).
- **Automated Test Suite:** 35+ automated pytest tests covering indices, area stats, transition matrices, georeferencing, and zero spatial leakage.
- **Defensive Programming:** Safe zero-division handling, matrix row normalization, nodata preservation, and custom exception classes.
- **Interactive UI:** 7-page Streamlit dashboard with Plotly charts, Folium geospatial raster overlays, and GeoTIFF downloads.
