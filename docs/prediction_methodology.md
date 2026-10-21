# Future LULC Prediction Methodology & Historical Backtesting

This document outlines the theoretical foundations, implementation details, and evaluation framework for future land-cover forecasting (2030, 2035) in Azamgarh District.

---

## 1. Mathematical Modeling Framework

### 1.1 First-Order Discrete-Time Markov Chain
Land-cover conversion is modeled as a stochastic process where the state at time $t + \Delta t$ depends solely on the state at time $t$ (Markovian memoryless property):
$$P(X_{t+1} = j \mid X_t = i, X_{t-1} = i_{t-1}, \dots) = P(X_{t+1} = j \mid X_t = i) = P_{ij}$$

The transition probability matrix $\mathbf{P} \in \mathbb{R}^{m \times m}$ is derived empirically from historical land-cover maps:
$$P_{ij} = \frac{N_{ij}}{\sum_{k=1}^m N_{ik}}$$
where $\sum_{j=1}^m P_{ij} = 1.0$ for all rows $i$.

The projected class area vector $\mathbf{v}_{t+n}$ after $n$ intervals is calculated as:
$$\mathbf{v}_{t+n} = \mathbf{v}_t \cdot \mathbf{P}^n$$

### 1.2 Cellular Automata Spatial Allocation (CA-Markov)
While standard Markov models accurately forecast the total quantum of class areas, they provide zero spatial information on *where* conversions will occur. We couple Markov transition probabilities with a spatial contiguity filter:
1. **Neighborhood Effect:** We compute a spatial convolution of class presence over a $5 \times 5$ Moore neighborhood ($24$ surrounding pixels).
2. **Transition Suitability:**
   $$\text{Suitability}_{ij}(x, y) = P_{ij} \times \left(1.0 + \alpha \cdot \text{Density}_j(x, y)\right)$$
3. **Spatial Aggregation:** Pixels adjacent to existing urban centers or existing orchards have a higher probability of conversion, matching real-world contiguous peri-urban expansion patterns observed along Azamgarh's arterial roads.

---

## 2. Mandatory Historical Backtesting Protocol

Claiming a future forecast without evaluating the model's predictive ability on past data is scientifically unsound. We implement a mandatory **three-epoch historical backtest**:

| Stage | Period | Function |
|---|---|---|
| **Calibration** | 2019 → 2022 | Estimate empirical transition matrix $\mathbf{P}_{19-22}$ and CA contiguity parameters. |
| **Simulation** | 2022 → 2025 | Run CA-Markov forward to 2025 in a blind forecast (without showing the model the true 2025 map). |
| **Validation** | 2025 | Pixel-by-pixel cross-tabulation of simulated 2025 vs actual independently classified 2025 map. |

### Evaluation Metrics Reported:
1. **Overall Spatial Agreement:**
   $$\text{Agreement} = \frac{\sum_{i=1}^m \text{Count}(\text{Simulated}_{2025} == \text{Actual}_{2025})}{N_{\text{total}}}$$
2. **Figure of Merit (FoM):**
   $$\text{FoM} = \frac{B}{A + B + C + D}$$
   where:
   - $B$ = Observed change correctly predicted as change (Hits)
   - $A$ = Observed change predicted as persistence (Misses)
   - $C$ = Persistence predicted as change (False alarms)
   - $D$ = Observed change predicted as wrong class of change

---

## 3. Assumptions, Limitations & Uncertainties

1. **Stationarity Assumption:** The model assumes that the drivers of land conversion observed between 2019 and 2025 (population growth, agricultural mechanization, brick kiln expansion) will continue at constant rates through 2030 and 2035.
2. **Exogenous Policy Shocks:** The model cannot anticipate external socio-economic interventions, such as new government industrial corridors, major bypass highways, or new canal infrastructure.
3. **Cumulative Error Propagation:** Any classification error in the baseline 2025 map will propagate into the 2030 and 2035 projections.
4. **Transparent Presentation:** Future maps must always be explicitly labeled as **"Model-Based Exploratory Projections"**, never as actual future observations.
