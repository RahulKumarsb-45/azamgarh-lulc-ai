"""Unit tests for change detection, cross-tabulation, critical transitions, and hotspot density."""
import numpy as np
import pytest

from src.analysis.change_detection import (
    detect_land_cover_changes,
    extract_critical_transitions,
    identify_change_hotspots,
)


def test_detect_land_cover_changes():
    m1 = np.ones((10, 10), dtype=np.int32)
    m2 = m1.copy()
    m2[0:2, 0:2] = 4  # 4 pixels changed from 1 -> 4

    change_mask, trans_df = detect_land_cover_changes(m1, m2)
    assert change_mask.shape == (10, 10)
    assert np.sum(change_mask) == 4

    # 4 pixels changed
    assert not trans_df.empty
    trans_1_to_4 = trans_df[(trans_df["from_code"] == 1) & (trans_df["to_code"] == 4)].iloc[0]
    assert trans_1_to_4["pixel_count"] == 4
    assert bool(trans_1_to_4["is_change"]) is True

    # 96 pixels unchanged
    trans_1_to_1 = trans_df[(trans_df["from_code"] == 1) & (trans_df["to_code"] == 1)].iloc[0]
    assert trans_1_to_1["pixel_count"] == 96
    assert bool(trans_1_to_1["is_change"]) is False


def test_extract_critical_transitions():
    m1 = np.ones((20, 20), dtype=np.int32)
    m2 = m1.copy()
    m2[0:5, 0:5] = 4  # 25 pixels 1 -> 4
    m2[5:7, 5:7] = 2  # 4 pixels 1 -> 2

    _, trans_df = detect_land_cover_changes(m1, m2)
    crit = extract_critical_transitions(trans_df, total_reference_area_km2=4000.0)

    assert not crit.empty
    assert "estimated_area_km2" in crit.columns
    assert "estimated_area_ha" in crit.columns
    # 25 pixels out of 400 = 6.25% of 4000 = 250 km²
    top_change = crit.iloc[0]
    assert top_change["from_code"] == 1
    assert top_change["to_code"] == 4
    assert pytest.approx(top_change["estimated_area_km2"], 0.1) == 250.0
    assert pytest.approx(top_change["estimated_area_ha"], 10.0) == 25000.0


def test_identify_change_hotspots():
    change_mask = np.zeros((30, 30), dtype=np.uint8)
    # Dense block of changes in upper left
    change_mask[2:10, 2:10] = 1

    density_pct, hotspot_mask = identify_change_hotspots(change_mask, kernel_size=5, hotspot_threshold_pct=50.0)
    assert density_pct.shape == (30, 30)
    assert hotspot_mask.shape == (30, 30)
    assert np.max(density_pct) > 50.0
    assert np.sum(hotspot_mask) > 0
