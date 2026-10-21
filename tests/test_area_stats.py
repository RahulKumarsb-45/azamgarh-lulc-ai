"""Unit tests for area calculation, metric/hectare units, and gain/loss transitions."""
import numpy as np
import pytest

from src.analysis.area_stats import (
    calculate_class_areas,
    calculate_gain_loss,
    summarize_multi_year_areas,
)


def test_calculate_class_areas_conservation_and_hectares():
    # 50x50 map
    grid = np.ones((50, 50), dtype=np.int32)
    grid[0:10, :] = 2   # 500 pixels of class 2
    grid[10:20, :] = 3  # 500 pixels of class 3
    grid[20:30, :] = 4  # 500 pixels of class 4
    grid[30:35, :] = 5  # 250 pixels of class 5
    # Remaining 750 pixels = class 1

    df = calculate_class_areas(grid, total_reference_area_km2=4054.0)
    assert not df.empty
    assert "area_km2" in df.columns
    assert "area_ha" in df.columns
    assert "percentage" in df.columns

    # Check 1 km² = 100 hectares relation
    for _, row in df.iterrows():
        assert pytest.approx(row["area_ha"], 0.01) == row["area_km2"] * 100.0

    # Percentages must sum strictly to 100%
    assert pytest.approx(df["percentage"].sum(), 0.01) == 100.0
    # Area in km² must sum strictly to reference area
    assert pytest.approx(df["area_km2"].sum(), 0.05) == 4054.0


def test_calculate_gain_loss():
    grid_t1 = np.ones((20, 20), dtype=np.int32)
    grid_t2 = grid_t1.copy()
    grid_t2[0:5, 0:5] = 4  # 25 pixels converted 1 -> 4

    df1 = calculate_class_areas(grid_t1, total_reference_area_km2=4000.0)
    df2 = calculate_class_areas(grid_t2, total_reference_area_km2=4000.0)

    gl = calculate_gain_loss(df1, df2, year_t1=2019, year_t2=2025)
    assert "abs_change_km2" in gl.columns
    assert "abs_change_ha" in gl.columns
    assert "trend" in gl.columns

    # Class 4 (built-up) should show expansion
    c4 = gl[gl["class_code"] == 4].iloc[0]
    assert c4["abs_change_km2"] > 0
    assert c4["abs_change_ha"] > 0
    assert c4["trend"] == "Expansion"

    # Class 1 (cropland) should show decline
    c1 = gl[gl["class_code"] == 1].iloc[0]
    assert c1["abs_change_km2"] < 0
    assert c1["abs_change_ha"] < 0
    assert c1["trend"] == "Decline"


def test_calculate_class_areas_raw_pixel_mode():
    """Verify raw pixel area computation when total_reference_area_km2 is None."""
    # 10x10 map of 20m pixels: 100 pixels * (20*20 m² = 400 m² = 0.0004 km²) = 0.04 km²
    grid = np.ones((10, 10), dtype=np.int32)
    grid[0:5, :] = 2  # 50 pixels of class 2, 50 pixels of class 1

    df = calculate_class_areas(grid, pixel_size_m=20.0, total_reference_area_km2=None)
    assert not df.empty
    c1 = df[df["class_code"] == 1].iloc[0]
    c2 = df[df["class_code"] == 2].iloc[0]

    # 50 * 0.0004 = 0.02 km² = 2.0 ha
    assert pytest.approx(c1["area_km2"], 0.001) == 0.02
    assert pytest.approx(c1["area_ha"], 0.1) == 2.0
    assert pytest.approx(c2["area_km2"], 0.001) == 0.02
    assert pytest.approx(df["percentage"].sum(), 0.01) == 100.0


def test_summarize_multi_year_areas():
    """Verify multi-year trajectory summarization and schema."""
    maps = {
        2019: np.ones((10, 10), dtype=np.int32),
        2022: np.ones((10, 10), dtype=np.int32) * 2,
        2025: np.ones((10, 10), dtype=np.int32) * 4,
    }
    summary = summarize_multi_year_areas(maps, total_reference_area_km2=4054.0)
    assert not summary.empty
    assert "year" in summary.columns
    assert set(summary["year"].unique()) == {2019, 2022, 2025}
    # 5 classes * 3 years = 15 records
    assert len(summary) == 15

