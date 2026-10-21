"""Independent validation and accuracy assessment module.

Computes:
- Error matrix (Confusion Matrix)
- Overall Accuracy (OA)
- User's Accuracy (Precision) and Commission Error (1 - UA)
- Producer's Accuracy (Recall) and Omission Error (1 - PA)
- F1-Score per class
- Cohen's Kappa Coefficient
- Area-adjusted accuracy and area estimates with 95% confidence intervals
  following Olofsson et al. (2014), 'Good practices for estimating area and
  assessing accuracy of land change', Remote Sensing of Environment.
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
from sklearn.metrics import confusion_matrix, cohen_kappa_score


DEFAULT_CLASS_NAMES = {
    1: "Agriculture / Cropland",
    2: "Vegetation",
    3: "Water Bodies",
    4: "Built-up Areas",
    5: "Barren / Open Land",
}


def evaluate_classification(
    y_true: np.ndarray | pd.Series,
    y_pred: np.ndarray | pd.Series,
    class_names: dict[int, str] | None = None,
) -> dict:
    """Calculate sample-based confusion matrix, OA, PA, UA, F1, and Kappa."""
    names = class_names or DEFAULT_CLASS_NAMES
    classes = sorted(names.keys())

    y_t = np.asarray(y_true)
    y_p = np.asarray(y_pred)

    cm = confusion_matrix(y_t, y_p, labels=classes)

    total_samples = int(np.sum(cm))
    correct = int(np.trace(cm))
    overall_accuracy = correct / total_samples if total_samples > 0 else 0.0

    kappa = cohen_kappa_score(y_t, y_p, labels=classes)

    per_class = []
    for idx, c in enumerate(classes):
        tp = int(cm[idx, idx])
        ref_total = int(np.sum(cm[idx, :]))    # row sum = reference count
        map_total = int(np.sum(cm[:, idx]))    # col sum = predicted count

        # Producer's Accuracy (Recall)
        pa = tp / ref_total if ref_total > 0 else 0.0
        # User's Accuracy (Precision)
        ua = tp / map_total if map_total > 0 else 0.0

        omission_error = 1.0 - pa
        commission_error = 1.0 - ua

        f1 = (2 * pa * ua) / (pa + ua) if (pa + ua) > 0 else 0.0

        per_class.append({
            "class_code": c,
            "class_name": names.get(c, f"Class {c}"),
            "reference_count": ref_total,
            "mapped_count": map_total,
            "true_positive": tp,
            "producers_accuracy": round(pa, 4),
            "users_accuracy": round(ua, 4),
            "omission_error": round(omission_error, 4),
            "commission_error": round(commission_error, 4),
            "f1_score": round(f1, 4),
        })

    cm_df = pd.DataFrame(
        cm,
        index=[f"Ref: {names.get(c, c)}" for c in classes],
        columns=[f"Map: {names.get(c, c)}" for c in classes],
    )

    metrics_df = pd.DataFrame(per_class)

    return {
        "overall_accuracy": round(overall_accuracy, 4),
        "overall_accuracy_pct": round(overall_accuracy * 100.0, 2),
        "cohens_kappa": round(float(kappa), 4),
        "total_validation_samples": total_samples,
        "confusion_matrix": cm_df,
        "raw_confusion_matrix": cm,
        "class_metrics": metrics_df,
        "classes": classes,
    }


def compute_olofsson_adjusted_areas(
    cm_sample: np.ndarray,
    mapped_area_km2_by_class: dict[int, float],
    classes: list[int] | None = None,
    class_names: dict[int, str] | None = None,
    matrix_orientation: str = "map_rows",
    z_score: float = 1.96,  # 95% confidence interval
) -> pd.DataFrame:
    """Compute area-adjusted accuracy and adjusted class areas (Olofsson et al. 2014).

    Accounts for stratified sampling where classes have unequal landscape area proportions.

    Args:
        cm_sample: Confusion matrix.
        mapped_area_km2_by_class: Total mapped area (km²) per class.
        classes: Ordered list of integer class codes.
        class_names: Mapping of class code to readable name.
        matrix_orientation: 'map_rows' (default for Olofsson: rows=map, cols=ref) or
                            'ref_rows' (scikit-learn default: rows=ref, cols=map).
                            If 'ref_rows', the matrix is transposed to align with Olofsson strata.
        z_score: Critical value for confidence interval (default 1.96 for 95% CI).
    """
    classes = classes or sorted(mapped_area_km2_by_class.keys())
    names = class_names or DEFAULT_CLASS_NAMES

    total_area_km2 = sum(mapped_area_km2_by_class[c] for c in classes)
    W = np.array([mapped_area_km2_by_class[c] / total_area_km2 for c in classes], dtype=float)

    k = len(classes)
    raw_cm = np.asarray(cm_sample, dtype=float)

    # In Olofsson et al. (2014), strata are map classes (rows i), columns j are reference classes.
    if matrix_orientation == "ref_rows":
        n = raw_cm.T
    else:
        n = raw_cm

    # Row totals (n_i.) = sample count in map stratum i
    n_row = np.sum(n, axis=1)

    # Sample proportion matrix p_hat_ij = W_i * (n_ij / n_i.)
    p_hat = np.zeros((k, k), dtype=float)
    for i in range(k):
        if n_row[i] > 0:
            p_hat[i, :] = W[i] * (n[i, :] / n_row[i])
        else:
            p_hat[i, :] = 0.0

    # Adjusted overall accuracy: sum of diagonal of p_hat
    oa_adjusted = float(np.trace(p_hat))

    # Adjusted class areas: A_hat_j = total_area * sum_i(p_hat_ij)
    adjusted_prop = np.sum(p_hat, axis=0)
    adjusted_area_km2 = total_area_km2 * adjusted_prop

    # Standard error of area estimates (Olofsson et al. 2014, Eq. 10)
    se_area = np.zeros(k, dtype=float)
    for j in range(k):
        var_sum = 0.0
        for i in range(k):
            if n_row[i] > 1:
                p_ij = n[i, j] / n_row[i]
                var_sum += (W[i] ** 2) * (p_ij * (1.0 - p_ij)) / (n_row[i] - 1)
        se_area[j] = total_area_km2 * np.sqrt(max(0.0, var_sum))

    # Producer's and User's accuracy adjusted
    results = []
    for idx, c in enumerate(classes):
        # User's accuracy = p_hat_ii / W_i
        ua_adj = p_hat[idx, idx] / W[idx] if W[idx] > 0 else 0.0
        # Producer's accuracy = p_hat_jj / sum_i(p_hat_ij)
        pa_adj = p_hat[idx, idx] / adjusted_prop[idx] if adjusted_prop[idx] > 0 else 0.0

        ci_lower = max(0.0, adjusted_area_km2[idx] - z_score * se_area[idx])
        ci_upper = adjusted_area_km2[idx] + z_score * se_area[idx]

        results.append({
            "class_code": c,
            "class_name": names.get(c, f"Class {c}"),
            "mapped_area_km2": round(float(mapped_area_km2_by_class[c]), 2),
            "mapped_pct": round(float(W[idx] * 100.0), 2),
            "adjusted_area_km2": round(float(adjusted_area_km2[idx]), 2),
            "adjusted_pct": round(float(adjusted_prop[idx] * 100.0), 2),
            "se_area_km2": round(float(se_area[idx]), 2),
            "ci_95_lower_km2": round(float(ci_lower), 2),
            "ci_95_upper_km2": round(float(ci_upper), 2),
            "producers_accuracy_adjusted": round(float(pa_adj), 4),
            "users_accuracy_adjusted": round(float(ua_adj), 4),
        })

    df = pd.DataFrame(results)
    df.attrs["overall_accuracy_adjusted"] = round(oa_adjusted, 4)
    df.attrs["overall_accuracy_adjusted_pct"] = round(oa_adjusted * 100.0, 2)
    df.attrs["total_study_area_km2"] = round(total_area_km2, 2)
    return df
