# Independent Validation & Sampling Protocol

This protocol defines the sampling design, spatial partitioning rules, dual-reviewer agreement procedures, and accuracy metrics implemented to ensure scientific integrity and academic rigor.

---

## 1. The Spatial Leakage Problem in Satellite ML

In terrestrial remote sensing, nearby pixels exhibit high spatial autocorrelation:
$$\operatorname{Cov}(Z(s_1), Z(s_2)) > 0 \quad \text{for small } \|s_1 - s_2\|$$
If validation samples are chosen by naive random pixel splitting (e.g. 80/20 train/test on adjacent pixels), the classifier's test set will contain pixels located within meters of training pixels. The resulting "accuracy" simply measures local interpolation rather than genuine geographic generalization.

### Solution: Spatial Block Partitioning
1. The study area bounding box ($82.80^\circ \text{E}$ to $83.65^\circ \text{E}$, $25.70^\circ \text{N}$ to $26.35^\circ \text{N}$) is discretized into regular **$5\text{ km} \times 5\text{ km}$ spatial grid blocks**.
2. Entire spatial blocks are randomly assigned to either `train` (70%) or `val` (30%).
3. **Rigorous Criterion:** All reference points falling within a training block are strictly excluded from validation:
   $$\mathcal{B}_{\text{train}} \cap \mathcal{B}_{\text{val}} = \emptyset$$

---

## 2. Stratified Sampling Design

To ensure statistical power across both dominant classes (Cropland ~74%) and rare classes (Water Bodies ~2%, Barren ~2%):
- Sampling is stratified across all 5 classes.
- Target: **$\ge 50$ independently interpreted reference points per class** (following Congalton 1991).
- Metadata tracked per reference point:
  - `sample_id`
  - `lon`, `lat` (WGS-84)
  - `spatial_block_id`
  - `reference_year`
  - `reviewer_1_code`
  - `reviewer_2_code`
  - `resolved_code`
  - `confidence_score` (High / Medium / Low)

---

## 3. Dual-Interpreter Protocol

To eliminate individual human visual bias:
1. **Member 1 (Remote Sensing Specialist)** and **Member 2 (Integration & Data Specialist)** independently interpret every validation point using same-year Sentinel-2 seasonal composites and dated high-resolution base imagery.
2. Inter-rater agreement is calculated using Cohen's Kappa ($\kappa$):
   $$\kappa_{\text{inter}} = \frac{p_o - p_e}{1 - p_e}$$
3. Any point where Member 1 and Member 2 disagree is flagged for joint review. If the point remains ambiguous (e.g., highly mixed pixel at an orchard-crop boundary), it is excluded rather than guessed.

---

## 4. Accuracy Assessment Metrics

From the validation error matrix (where $n_{ij}$ represents reference class $i$ classified as map class $j$):

1. **Overall Accuracy (OA):**
   $$\text{OA} = \frac{\sum_{i=1}^k n_{ii}}{N}$$

2. **Producer's Accuracy (PA / Recall):**
   $$\text{PA}_i = \frac{n_{ii}}{n_{i\cdot}} \quad (\text{Omission Error} = 1 - \text{PA}_i)$$

3. **User's Accuracy (UA / Precision):**
   $$\text{UA}_j = \frac{n_{jj}}{n_{\cdot j}} \quad (\text{Commission Error} = 1 - \text{UA}_j)$$

4. **F1-Score:**
   $$\text{F1}_i = \frac{2 \cdot \text{PA}_i \cdot \text{UA}_i}{\text{PA}_i + \text{UA}_i}$$

5. **Cohen's Kappa Coefficient ($\kappa$):**
   $$\kappa = \frac{N \sum_{i=1}^k n_{ii} - \sum_{i=1}^k (n_{i\cdot} n_{\cdot i})}{N^2 - \sum_{i=1}^k (n_{i\cdot} n_{\cdot i})}$$

---

## 5. Area-Adjusted Accuracy & Standard Error (Olofsson et al. 2014)

Because map classes occupy unequal proportions of the landscape ($W_i = A_i / A_{\text{total}}$), sample proportions are converted to population area proportions:
$$\hat{p}_{ij} = W_i \cdot \frac{n_{ij}}{n_{i\cdot}}$$

- **Adjusted Overall Accuracy:** $\hat{\text{OA}} = \sum_{i=1}^k \hat{p}_{ii}$
- **Adjusted Class Area:** $\hat{A}_j = A_{\text{total}} \cdot \sum_{i=1}^k \hat{p}_{ij}$
- **Standard Error of Area Estimate:**
  $$S(\hat{A}_j) = A_{\text{total}} \sqrt{\sum_{i=1}^k W_i^2 \frac{\frac{n_{ij}}{n_{i\cdot}} \left(1 - \frac{n_{ij}}{n_{i\cdot}}\right)}{n_{i\cdot} - 1}}$$
- **95% Confidence Interval:** $\hat{A}_j \pm 1.96 \cdot S(\hat{A}_j)$
