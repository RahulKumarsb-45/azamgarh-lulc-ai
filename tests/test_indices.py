"""Unit tests for spectral indices (NDVI, NDWI, MNDWI, NDBI) and phenological features."""
import numpy as np
import pandas as pd
import pytest

from src.features.indices import (
    calculate_indices,
    calculate_mndwi,
    calculate_ndbi,
    calculate_ndvi,
    calculate_ndwi,
    calculate_seasonal_metrics,
    safe_normalized_difference,
)


def test_safe_normalized_difference_division_by_zero():
    # Sum is zero
    val = safe_normalized_difference(0.0, 0.0)
    assert val == 0.0

    # Array with zeros
    arr_a = np.array([0.0, 0.5, 0.0])
    arr_b = np.array([0.0, 0.5, 0.0])
    res = safe_normalized_difference(arr_a, arr_b)
    assert res[0] == 0.0
    assert pytest.approx(res[1]) == 0.0
    assert res[2] == 0.0

    # Series with NaNs
    s_a = pd.Series([np.nan, 0.4, 0.0])
    s_b = pd.Series([0.2, np.nan, 0.0])
    s_res = safe_normalized_difference(s_a, s_b)
    assert s_res.iloc[0] == 0.0
    assert s_res.iloc[1] == 0.0
    assert s_res.iloc[2] == 0.0


def test_calculate_ndvi():
    nir = np.array([0.45, 0.02, 0.38])
    red = np.array([0.05, 0.05, 0.08])
    ndvi = calculate_ndvi(nir, red)
    assert len(ndvi) == 3
    # Healthy vegetation NIR >> Red -> NDVI should be high (~0.8)
    assert ndvi[0] > 0.7
    # Water Red > NIR -> NDVI should be negative
    assert ndvi[1] < 0.0


def test_calculate_mndwi():
    # Water: high green (0.15), low SWIR1 (0.01) -> MNDWI > 0
    green = np.array([0.15, 0.05])
    swir1 = np.array([0.01, 0.30])
    mndwi = calculate_mndwi(green, swir1)
    assert mndwi[0] > 0.8
    # Built-up / dry soil: low green, high SWIR1 -> MNDWI strongly negative
    assert mndwi[1] < -0.5


def test_calculate_ndwi():
    # Water: high green (0.12), low NIR (0.02) -> NDWI > 0
    green = np.array([0.12, 0.04])
    nir = np.array([0.02, 0.40])
    ndwi = calculate_ndwi(green, nir)
    assert ndwi[0] > 0.6
    # Vegetation: green < NIR -> NDWI negative
    assert ndwi[1] < -0.6


def test_calculate_ndbi():
    # Built-up: SWIR1 (0.30) > NIR (0.18) -> NDBI > 0
    swir1 = np.array([0.30, 0.12])
    nir = np.array([0.18, 0.45])
    ndbi = calculate_ndbi(swir1, nir)
    assert ndbi[0] > 0.2
    # Dense vegetation: NIR >> SWIR1 -> NDBI strongly negative
    assert ndbi[1] < -0.5



def test_calculate_indices_dataframe():
    df = pd.DataFrame({
        "B2": [0.03, 0.08],
        "B3": [0.06, 0.09],
        "B4": [0.04, 0.05],
        "B8": [0.45, 0.02],
        "B11": [0.14, 0.01],
        "B12": [0.07, 0.01],
    })
    res = calculate_indices(df)
    assert "NDVI" in res.columns
    assert "NDWI" in res.columns
    assert "MNDWI" in res.columns
    assert "NDBI" in res.columns
    assert "NIR_SWIR_Ratio" in res.columns
    assert "Green_Red_Ratio" in res.columns


def test_seasonal_metrics():
    rabi = np.array([0.75, 0.60])
    zaid = np.array([0.25, 0.55])
    metrics = calculate_seasonal_metrics(rabi, zaid)
    # Cropland swing (0.75 - 0.25 = 0.50) should be much higher than vegetation (0.60 - 0.55 = 0.05)
    assert metrics["ndvi_swing"][0] > metrics["ndvi_swing"][1]
    assert pytest.approx(metrics["ndvi_swing"][0], 0.001) == 0.50
