# Scientific Methodology & Technical Workflow

This document details the scientific principles, mathematical formulations, and engineering architecture implemented for the **Azamgarh District LULC Classification and Future Prediction System**.

---

## 1. Study Area Geographical Setting

**Azamgarh District** is located in the eastern alluvial plains of Uttar Pradesh, India, within the Indo-Gangetic basin. The region is predominantly flat, fertile, and intensively cultivated, with the **Tamsa River** traversing the district. 
- **Latitude:** ~25°38' N to 26°27' N
- **Longitude:** ~82°40' E to 83°52' E
- **Climate:** Subtropical monsoon climate characterized by hot summers, heavy monsoon rains (July–September), and mild dry winters.
- **Agricultural Phenology:**
  1. *Rabi season (November–April):* Wheat, mustard, pulses, potato (harvested March–April).
  2. *Zaid season (April–June):* Pre-monsoon dry period; fields largely fallow with localized cucurbits/fodder crops.
  3. *Kharif season (July–November):* Paddy rice, maize, sugarcane (peak maturity October–November).

---

## 2. Standardized Five-Class Schema

To avoid classification ambiguity and maintain high academic defensibility, we define a 5-class schema:

| Code | Class Name | Hex Color | Scientific Definition | Diagnostic Spectral / Phenological Behavior |
|---|---|---|---|---|
| **1** | **Agriculture / Cropland** | `#F2D16B` | Arable land under active cultivation or seasonal fallow. | Strong seasonal NDVI swing across Rabi peak (NDVI ~0.70) and Zaid post-harvest (NDVI ~0.20). |
| **2** | **Vegetation** | `#2E7D32` | Perennial tree canopy, mango/guava orchards, rural groves, canal plantations. | Persistently high NDVI (>0.60) across all seasons with minimal seasonal swing. |
| **3** | **Water Bodies** | `#1E88E5` | Tamsa River channel, oxbow lakes (taal), village ponds (pokhari), irrigation canals. | Strongly negative NDVI (<0.0), positive NDWI (>0.05), very low NIR/SWIR reflectance. |
| **4** | **Built-up Areas** | `#D32F2F` | Azamgarh city urban core, tehsil headquarters, rural homesteads, paved highways, impervious surfaces. | High SWIR-1 (B11) and Red (B4) reflectance, positive NDBI (>0.0), low-to-moderate NDVI. |
| **5** | **Barren / Open Land** | `#A1887F` | Exposed dry soil, riverbed sandbanks, uncultivated wasteland bare throughout all seasons. | Low NDVI (<0.25) across ALL seasons without seasonal crop greening; high SWIR reflectance. |

### Resolving the Cropland vs. Perennial Tree Cover vs. Barren Ambiguity
A common pitfall in remote sensing is using a single-date NDVI threshold, which confuses harvested cropland with barren land, or lush summer orchards with mature crops. We resolve this by incorporating **multi-temporal seasonal phenology**:
$$\Delta \text{NDVI}_{\text{swing}} = \text{NDVI}_{\text{Rabi}} - \text{NDVI}_{\text{Zaid}}$$
- **Cropland:** $\Delta \text{NDVI} > 0.35$ (dramatic seasonal harvest swing).
- **Perennial Trees:** $\text{NDVI}_{\text{Zaid}} > 0.50$ and $\Delta \text{NDVI} < 0.20$ (sustained foliage).
- **Barren Land:** $\text{NDVI}_{\text{Rabi}} < 0.25$ and $\text{NDVI}_{\text{Zaid}} < 0.25$ (perennially bare).

---

## 3. Spectral Indices

We calculate three validated normalized difference indices from Sentinel-2 MSI surface reflectance:

1. **Normalized Difference Vegetation Index (NDVI)** [Rouse et al. 1974]:
   $$\text{NDVI} = \frac{\text{B8 (NIR)} - \text{B4 (Red)}}{\text{B8 (NIR)} + \text{B4 (Red)}}$$

2. **Normalized Difference Water Index (NDWI)** [McFeeters 1996]:
   $$\text{NDWI} = \frac{\text{B3 (Green)} - \text{B8 (NIR)}}{\text{B3 (Green)} + \text{B8 (NIR)}}$$
   *(Note: Explicitly using McFeeters 1996 rather than Gao 1996 to optimize open waterbody delineation).*

3. **Normalized Difference Built-up Index (NDBI)** [Zha et al. 2003]:
   $$\text{NDBI} = \frac{\text{B11 (SWIR1)} - \text{B8 (NIR)}}{\text{B11 (SWIR1)} + \text{B8 (NIR)}}$$

---

## 4. Supervised Machine Learning: Random Forest

We employ an ensemble Random Forest classifier:
- **Decision Trees:** $N = 100$ trees.
- **Splitting Criterion:** Gini impurity.
- **Input Features (9 Bands/Indices):**
  $$\mathbf{X} = [B_2, B_3, B_4, B_8, B_{11}, B_{12}, \text{NDVI}, \text{NDWI}, \text{NDBI}]$$
- **Feature Importance:** Gini feature importance evaluates the relative contribution of SWIR and vegetation indices in separating impervious settlements from dry fallow soils.

---

## 5. Markov Chain & Cellular Automata (CA-Markov) Modeling

### 5.1 First-Order Markov Transition Matrix
The transition probability from state $i$ to state $j$ over time step $\Delta t$ is estimated as:
$$P_{ij} = \frac{N_{ij}}{\sum_{k=1}^m N_{ik}}$$
where $N_{ij}$ is the number of pixels transitioning from class $i$ to class $j$, satisfying row-stochasticity $\sum_j P_{ij} = 1.0$.

Future state area vector $\mathbf{v}_{t+n}$ is projected as:
$$\mathbf{v}_{t+n} = \mathbf{v}_t \cdot \mathbf{P}^n$$

### 5.2 Cellular Automata Spatial Simulation
While standard Markov models predict total class areas, they lack spatial explicit allocation. We couple Markov transition probabilities with a spatial Cellular Automata contiguity kernel (Moore neighborhood):
$$S_{ij}(x, y) = P_{ij} \times \left(1 + \gamma \cdot \frac{1}{K^2 - 1} \sum_{(u, v) \in \mathcal{N}} I(L(u, v) = j)\right)$$
where $L(u, v)$ is the neighboring land cover class, favoring the realistic aggregation of expanding built-up settlements and contiguous agroforestry orchards.
