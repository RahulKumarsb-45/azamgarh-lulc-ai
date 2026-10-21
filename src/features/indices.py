"""Spectral index calculations and seasonal feature engineering.

Formulas:
- NDVI = (NIR - Red) / (NIR + Red) = (B8 - B4) / (B8 + B4) [Rouse et al. 1974]
- NDWI = (Green - NIR) / (Green + NIR) = (B3 - B8) / (B3 + B8) [McFeeters 1996]
- MNDWI = (Green - SWIR1) / (Green + SWIR1) = (B3 - B11) / (B3 + B11) [Xu 2006]
- NDBI = (SWIR1 - NIR) / (SWIR1 + NIR) = (B11 - B8) / (B11 + B8) [Zha et al. 2003]

Includes seasonal phenological swing features to distinguish:
- Cropland (large NDVI swing between peak rabi crop and bare zaid fallow)
- Perennial vegetation (high NDVI in all seasons, low swing)
- Barren land (low NDVI across all seasons)
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


def safe_normalized_difference(
    band_a: np.ndarray | pd.Series | float,
    band_b: np.ndarray | pd.Series | float,
    eps: float = 1e-6,
) -> np.ndarray | pd.Series | float:
    """Compute (band_a - band_b) / (band_a + band_b) safely handling zero sums and NaNs."""
    if isinstance(band_a, pd.Series) or isinstance(band_b, pd.Series):
        s_a = pd.Series(band_a).astype(float)
        s_b = pd.Series(band_b).astype(float)
        denom = s_a + s_b
        zero_or_nan = (denom.abs() < eps) | denom.isna()
        safe_denom = denom.where(~zero_or_nan, 1.0)
        res = (s_a - s_b) / safe_denom
        res = res.where(~zero_or_nan, 0.0)
        return res.clip(-1.0, 1.0)

    if isinstance(band_a, np.ndarray) or isinstance(band_b, np.ndarray):
        arr_a = np.asarray(band_a, dtype=float)
        arr_b = np.asarray(band_b, dtype=float)
        denom = arr_a + arr_b
        zero_or_nan = (np.abs(denom) < eps) | np.isnan(denom)
        safe_denom = np.where(zero_or_nan, 1.0, denom)
        res = (arr_a - arr_b) / safe_denom
        res = np.where(zero_or_nan, 0.0, res)
        return np.clip(res, -1.0, 1.0)

    # Scalar float
    a = float(band_a)
    b = float(band_b)
    denom = a + b
    if abs(denom) < eps or np.isnan(denom):
        return 0.0
    val = (a - b) / denom
    return max(-1.0, min(1.0, val))


def calculate_ndvi(nir: np.ndarray | pd.Series | float, red: np.ndarray | pd.Series | float) -> np.ndarray | pd.Series | float:
    """Normalized Difference Vegetation Index (Rouse et al. 1974)."""
    return safe_normalized_difference(nir, red)


def calculate_ndwi(green: np.ndarray | pd.Series | float, nir: np.ndarray | pd.Series | float) -> np.ndarray | pd.Series | float:
    """Normalized Difference Water Index (McFeeters 1996)."""
    return safe_normalized_difference(green, nir)


def calculate_mndwi(green: np.ndarray | pd.Series | float, swir1: np.ndarray | pd.Series | float) -> np.ndarray | pd.Series | float:
    """Modified Normalized Difference Water Index (Xu 2006).

    Uses SWIR1 instead of NIR to suppress built-up noise and sharply delineate open waterbodies.
    """
    return safe_normalized_difference(green, swir1)


def calculate_ndbi(swir1: np.ndarray | pd.Series | float, nir: np.ndarray | pd.Series | float) -> np.ndarray | pd.Series | float:
    """Normalized Difference Built-up Index (Zha et al. 2003)."""
    return safe_normalized_difference(swir1, nir)


def calculate_indices(
    df_or_dict: pd.DataFrame | dict[str, np.ndarray],
    b_blue: str = "B2",
    b_green: str = "B3",
    b_red: str = "B4",
    b_nir: str = "B8",
    b_swir1: str = "B11",
    b_swir2: str = "B12",
) -> pd.DataFrame:
    """Calculate NDVI, NDWI, MNDWI, NDBI and spectral ratios for tabular or columnar data."""
    if isinstance(df_or_dict, dict):
        df = pd.DataFrame(df_or_dict)
    else:
        df = df_or_dict.copy()

    df["NDVI"] = calculate_ndvi(df[b_nir], df[b_red])
    df["NDWI"] = calculate_ndwi(df[b_green], df[b_nir])
    df["MNDWI"] = calculate_mndwi(df[b_green], df[b_swir1])
    df["NDBI"] = calculate_ndbi(df[b_swir1], df[b_nir])

    # Spectral ratios and differences for distinguishing soil vs impervious
    eps = 1e-6
    df["NIR_SWIR_Ratio"] = df[b_nir] / (df[b_swir1] + eps)
    df["Green_Red_Ratio"] = df[b_green] / (df[b_red] + eps)

    return df


def calculate_seasonal_metrics(
    ndvi_rabi: np.ndarray | pd.Series,
    ndvi_zaid: np.ndarray | pd.Series,
    ndvi_kharif: np.ndarray | pd.Series | None = None,
) -> dict[str, np.ndarray | pd.Series]:
    """Calculate phenological swing metrics across agricultural seasons.

    - Cropland exhibits high ndvi_swing (rabi - zaid).
    - Perennial vegetation maintains high ndvi_min and low swing.
    - Barren land maintains low ndvi_max.
    """
    ndvi_swing = ndvi_rabi - ndvi_zaid

    if ndvi_kharif is not None:
        if isinstance(ndvi_rabi, pd.Series):
            stacked = pd.concat([ndvi_rabi, ndvi_zaid, ndvi_kharif], axis=1)
            ndvi_min = stacked.min(axis=1)
            ndvi_max = stacked.max(axis=1)
            ndvi_mean = stacked.mean(axis=1)
        else:
            stacked = np.stack([ndvi_rabi, ndvi_zaid, ndvi_kharif], axis=0)
            ndvi_min = np.min(stacked, axis=0)
            ndvi_max = np.max(stacked, axis=0)
            ndvi_mean = np.mean(stacked, axis=0)
    else:
        if isinstance(ndvi_rabi, pd.Series):
            stacked = pd.concat([ndvi_rabi, ndvi_zaid], axis=1)
            ndvi_min = stacked.min(axis=1)
            ndvi_max = stacked.max(axis=1)
            ndvi_mean = stacked.mean(axis=1)
        else:
            stacked = np.stack([ndvi_rabi, ndvi_zaid], axis=0)
            ndvi_min = np.min(stacked, axis=0)
            ndvi_max = np.max(stacked, axis=0)
            ndvi_mean = np.mean(stacked, axis=0)

    return {
        "ndvi_swing": ndvi_swing,
        "ndvi_min": ndvi_min,
        "ndvi_max": ndvi_max,
        "ndvi_mean": ndvi_mean,
    }


def add_ee_indices(image):
    """Google Earth Engine helper to append standard indices to an ee.Image."""
    import ee

    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
    mndwi = image.normalizedDifference(["B3", "B11"]).rename("MNDWI")
    ndbi = image.normalizedDifference(["B11", "B8"]).rename("NDBI")
    return image.addBands([ndvi, ndwi, mndwi, ndbi])
