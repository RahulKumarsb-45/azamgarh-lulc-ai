"""Unit tests for independent validation, confusion matrix, and Olofsson area-adjusted accuracy."""
import numpy as np
import pytest

from src.models.validation import compute_olofsson_adjusted_areas, evaluate_classification


def test_evaluate_classification_perfect():
    y_true = np.array([1, 1, 2, 2, 3, 3, 4, 4, 5, 5])
    y_pred = np.array([1, 1, 2, 2, 3, 3, 4, 4, 5, 5])

    res = evaluate_classification(y_true, y_pred)
    assert res["overall_accuracy"] == 1.0
    assert res["overall_accuracy_pct"] == 100.0
    assert res["cohens_kappa"] == 1.0
    for _, row in res["class_metrics"].iterrows():
        assert row["producers_accuracy"] == 1.0
        assert row["users_accuracy"] == 1.0
        assert row["f1_score"] == 1.0


def test_evaluate_classification_with_errors():
    y_true = np.array([1, 1, 1, 2, 2, 3, 4, 5])
    y_pred = np.array([1, 1, 2, 2, 2, 3, 4, 4])  # 2 errors: 1->2 and 5->4

    res = evaluate_classification(y_true, y_pred)
    assert res["overall_accuracy"] == 6 / 8
    assert res["total_validation_samples"] == 8

    # Class 1 Producer's accuracy = 2 / 3
    c1 = res["class_metrics"][res["class_metrics"]["class_code"] == 1].iloc[0]
    assert pytest.approx(c1["producers_accuracy"], 0.001) == 2 / 3
    # Class 1 User's accuracy = 2 / 2 = 1.0
    assert c1["users_accuracy"] == 1.0


def test_olofsson_area_adjusted_accuracy():
    # 3-class test matrix
    cm = np.array([
        [80, 10, 10],
        [5,  85, 10],
        [10, 10, 80],
    ])
    mapped_areas = {1: 7000.0, 2: 2000.0, 3: 1000.0}

    adj_df = compute_olofsson_adjusted_areas(cm, mapped_areas, classes=[1, 2, 3])
    assert not adj_df.empty
    assert "adjusted_area_km2" in adj_df.columns
    assert "ci_95_lower_km2" in adj_df.columns
    assert "ci_95_upper_km2" in adj_df.columns

    # Adjusted areas should sum approximately to total mapped area
    total_mapped = sum(mapped_areas.values())
    total_adjusted = adj_df["adjusted_area_km2"].sum()
    assert pytest.approx(total_adjusted, 1.0) == total_mapped


def test_olofsson_ref_rows_orientation():
    """Verify Olofsson adjustment when confusion matrix is formatted as ref_rows."""
    cm_ref = np.array([
        [31, 0, 0, 0, 0],
        [0, 36, 0, 0, 0],
        [0, 0, 46, 0, 0],
        [0, 0, 0, 32, 9],
        [0, 0, 0, 5, 34],
    ])
    mapped_areas = {1: 2752.26, 2: 410.26, 3: 121.62, 4: 678.64, 5: 91.22}
    adj_df = compute_olofsson_adjusted_areas(cm_ref, mapped_areas, matrix_orientation="ref_rows")

    assert not adj_df.empty
    assert "se_area_km2" in adj_df.columns
    assert adj_df.attrs["overall_accuracy_adjusted_pct"] > 90.0
    # Cropland area should equal mapped area because zero errors
    c1 = adj_df[adj_df["class_code"] == 1].iloc[0]
    assert pytest.approx(c1["adjusted_area_km2"], 0.01) == 2752.26
    # Total adjusted area equals total mapped area
    assert pytest.approx(adj_df["adjusted_area_km2"].sum(), 0.1) == sum(mapped_areas.values())


def test_olofsson_zero_sample_stratum_handling():
    """Verify that Olofsson computation does not divide by zero when a stratum has 0 or 1 sample."""
    # Class 3 has 0 samples
    cm_sparse = np.array([
        [50, 0, 0],
        [0, 50, 0],
        [0,  0, 0],
    ])
    mapped_areas = {1: 3000.0, 2: 1000.0, 3: 54.0}
    adj_df = compute_olofsson_adjusted_areas(cm_sparse, mapped_areas, classes=[1, 2, 3])
    assert not adj_df.empty
    assert "se_area_km2" in adj_df.columns
    # Must sum to total mapped area without NaN
    assert not adj_df["adjusted_area_km2"].isna().any()
    assert not adj_df["se_area_km2"].isna().any()


