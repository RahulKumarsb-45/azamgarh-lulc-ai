"""Transition matrix computation, Markov chain projection, and CA-Markov simulation.

Supports:
- Empirical transition probability matrix calculation from observed raster pairs.
- Row-stochastic normalization and verification.
- Markov area projection: v_{t+n} = v_t * P^n.
- Cellular Automata spatial contiguity allocation (Moore neighbourhood).
- Historical backtesting (e.g. 2019 -> 2022 to simulate 2025, verified against observed 2025).
- Model evaluation: Overall Agreement, Kappa, and Figure of Merit (FoM).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root in sys.path
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import numpy as np
import pandas as pd
from scipy.signal import convolve2d
from sklearn.metrics import cohen_kappa_score, confusion_matrix


DEFAULT_CLASS_NAMES = {
    1: "Agriculture / Cropland",
    2: "Vegetation",
    3: "Water Bodies",
    4: "Built-up Areas",
    5: "Barren / Open Land",
}


def calculate_transition_matrix(
    map_t1: np.ndarray,
    map_t2: np.ndarray,
    classes: list[int] | None = None,
    class_names: dict[int, str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate pixel count transition matrix and row-stochastic probability matrix.

    Returns:
        (count_df, prob_df)
    """
    classes = classes or sorted(DEFAULT_CLASS_NAMES.keys())
    names = class_names or DEFAULT_CLASS_NAMES

    y1 = map_t1.flatten()
    y2 = map_t2.flatten()

    # Filter invalid/nodata
    valid = np.isin(y1, classes) & np.isin(y2, classes)
    y1_v = y1[valid]
    y2_v = y2[valid]

    cm = confusion_matrix(y1_v, y2_v, labels=classes)
    row_sums = cm.sum(axis=1, keepdims=True)

    # Transition probability P_ij = N_ij / N_i.
    with np.errstate(divide="ignore", invalid="ignore"):
        prob_mat = np.where(row_sums > 0, cm / row_sums, 0.0)

    # For empty rows or zero sums, set identity
    for i in range(len(classes)):
        if row_sums[i, 0] == 0:
            prob_mat[i, :] = 0.0
            prob_mat[i, i] = 1.0

    # Ensure exact row normalization
    prob_row_sums = prob_mat.sum(axis=1, keepdims=True)
    prob_mat = np.where(prob_row_sums > 0, prob_mat / prob_row_sums, prob_mat)

    labels = [names.get(c, f"Class {c}") for c in classes]
    count_df = pd.DataFrame(cm, index=[f"From: {l}" for l in labels], columns=[f"To: {l}" for l in labels])
    prob_df = pd.DataFrame(prob_mat, index=[f"From: {l}" for l in labels], columns=[f"To: {l}" for l in labels])

    return count_df, prob_df


def markov_prediction(
    initial_areas: dict[int, float],
    transition_prob_matrix: np.ndarray | pd.DataFrame,
    steps: int = 1,
    classes: list[int] | None = None,
) -> dict[int, float]:
    """Project class areas forward by n transition steps using Markov chain: v_{t+n} = v_t * P^n."""
    classes = classes or sorted(initial_areas.keys())
    if isinstance(transition_prob_matrix, pd.DataFrame):
        P = transition_prob_matrix.values
    else:
        P = np.asarray(transition_prob_matrix)

    # Matrix power for n steps
    Pn = np.linalg.matrix_power(P, steps)

    v0 = np.array([initial_areas[c] for c in classes], dtype=float)
    v_pred = np.dot(v0, Pn)

    total_init = sum(v0)
    total_pred = sum(v_pred)
    if total_pred > 0:
        v_pred = v_pred * (total_init / total_pred)  # ensure total area conservation

    return {c: round(float(v_pred[i]), 2) for i, c in enumerate(classes)}


def cellular_automata_markov_simulation(
    base_map: np.ndarray,
    transition_prob: np.ndarray | pd.DataFrame,
    iterations: int = 5,
    kernel_size: int = 5,
    classes: list[int] | None = None,
    seed: int = 42,
) -> np.ndarray:
    """Simulate spatial LULC allocation using Cellular Automata-Markov logic.

    Integrates:
    - First-order transition probabilities from historical change.
    - Spatial neighborhood suitability kernel (Moore neighbourhood) favoring
      aggregation of settlements and vegetation.
    """
    classes = classes or sorted(DEFAULT_CLASS_NAMES.keys())
    if isinstance(transition_prob, pd.DataFrame):
        P = transition_prob.values
    else:
        P = np.asarray(transition_prob)

    rng = np.random.default_rng(seed)
    current_map = base_map.copy()
    rows, cols = current_map.shape

    # 2D spatial contiguity kernel
    kernel = np.ones((kernel_size, kernel_size), dtype=float)
    kernel[kernel_size // 2, kernel_size // 2] = 0.0
    kernel /= kernel.sum()

    k_classes = len(classes)

    for step in range(iterations):
        # Calculate local neighborhood density for each class
        suitability_scores = np.zeros((k_classes, rows, cols), dtype=float)
        for i, c in enumerate(classes):
            binary_presence = (current_map == c).astype(float)
            suitability_scores[i] = convolve2d(binary_presence, kernel, mode="same", boundary="symm")

        # Combine transition probability with local suitability
        new_map = current_map.copy()
        for i, c_from in enumerate(classes):
            mask_from = (current_map == c_from)
            if not np.any(mask_from):
                continue

            for j, c_to in enumerate(classes):
                if c_from == c_to:
                    continue
                # Probability of transition adjusted by neighborhood suitability
                p_base = P[i, j]
                if p_base <= 0.001:
                    continue

                # CA rule: higher local presence of target class accelerates conversion
                local_force = suitability_scores[j][mask_from]
                trans_prob = p_base * (1.0 + 2.0 * local_force)

                random_draws = rng.random(size=np.sum(mask_from))
                transition_occurred = random_draws < (trans_prob / iterations)

                indices = np.where(mask_from)
                coords_y = indices[0][transition_occurred]
                coords_x = indices[1][transition_occurred]
                new_map[coords_y, coords_x] = c_to

        current_map = new_map

    return current_map


def run_historical_backtest(
    map_t1: np.ndarray,
    map_t2: np.ndarray,
    map_t3_actual: np.ndarray,
    years: tuple[int, int, int] = (2019, 2022, 2025),
    classes: list[int] | None = None,
    class_names: dict[int, str] | None = None,
) -> dict:
    """Historical backtesting evaluation.

    1. Calibrate transition matrix on map_t1 -> map_t2.
    2. Simulate forward to t3.
    3. Compare simulated t3 with actual classified t3.
    4. Compute Agreement, Confusion Matrix, Kappa, and Figure of Merit (FoM).
    """
    classes = classes or sorted(DEFAULT_CLASS_NAMES.keys())
    names = class_names or DEFAULT_CLASS_NAMES

    y1, y2, y3 = years
    step_test = y3 - y2

    # Calibrate on earlier period
    _, prob_df = calculate_transition_matrix(map_t1, map_t2, classes, names)

    # Simulate t3
    iterations = max(1, step_test)
    map_pred = cellular_automata_markov_simulation(
        base_map=map_t2,
        transition_prob=prob_df.values,
        iterations=iterations,
        classes=classes,
    )

    actual_flat = map_t3_actual.flatten()
    pred_flat = map_pred.flatten()

    valid = np.isin(actual_flat, classes) & np.isin(pred_flat, classes)
    act_v = actual_flat[valid]
    prd_v = pred_flat[valid]

    cm = confusion_matrix(act_v, prd_v, labels=classes)
    total_pixels = int(np.sum(cm))
    correct_pixels = int(np.trace(cm))
    overall_agreement = correct_pixels / total_pixels if total_pixels > 0 else 0.0

    kappa = cohen_kappa_score(act_v, prd_v, labels=classes)

    # Figure of Merit (FoM) = Correctly predicted changes / (Total observed changes + false change predictions)
    observed_changes = np.sum((actual_flat != map_t2.flatten()) & valid)
    predicted_changes = np.sum((pred_flat != map_t2.flatten()) & valid)
    correct_changes = np.sum((actual_flat != map_t2.flatten()) & (pred_flat == actual_flat) & valid)

    fom_denom = (observed_changes + predicted_changes - correct_changes)
    fom = float(correct_changes / fom_denom) if fom_denom > 0 else 0.0

    per_class_agreement = []
    for idx, c in enumerate(classes):
        tp = int(cm[idx, idx])
        ref_n = int(np.sum(cm[idx, :]))
        map_n = int(np.sum(cm[:, idx]))
        agreement_rate = tp / ref_n if ref_n > 0 else 0.0
        per_class_agreement.append({
            "class_code": c,
            "class_name": names.get(c, f"Class {c}"),
            "actual_pixels": ref_n,
            "predicted_pixels": map_n,
            "agreement_rate": round(agreement_rate, 4),
        })

    labels = [names.get(c, f"Class {c}") for c in classes]
    cm_df = pd.DataFrame(cm, index=[f"Actual: {l}" for l in labels], columns=[f"Predicted: {l}" for l in labels])

    return {
        "calibration_years": f"{y1} -> {y2}",
        "backtest_target_year": y3,
        "overall_agreement": round(overall_agreement, 4),
        "overall_agreement_pct": round(overall_agreement * 100.0, 2),
        "cohens_kappa": round(float(kappa), 4),
        "figure_of_merit": round(fom, 4),
        "confusion_matrix": cm_df,
        "class_agreement": pd.DataFrame(per_class_agreement),
        "predicted_map": map_pred,
        "actual_map": map_t3_actual,
    }
