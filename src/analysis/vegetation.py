"""Vegetation health dynamics, phenological cycle monitoring, and NDVI decline detection.

Scientific Note:
- In agricultural landscapes like Azamgarh District, strong seasonal NDVI fluctuations
  are dominated by crop rotation cycles (Rabi wheat vs Zaid fallow vs Kharif paddy).
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


def calculate_ndvi_summary_statistics(
    ndvi_array: np.ndarray,
    valid_range: tuple[float, float] = (-1.0, 1.0),
) -> dict[str, float]:
    """Calculate descriptive statistics for an NDVI raster layer."""
    flat = ndvi_array.flatten()
    valid = flat[(flat >= valid_range[0]) & (flat <= valid_range[1]) & ~np.isnan(flat)]

    if len(valid) == 0:
        return {
            "mean": 0.0, "median": 0.0, "std": 0.0,
            "min": 0.0, "max": 0.0, "p25": 0.0, "p75": 0.0,
        }

    return {
        "mean": round(float(np.mean(valid)), 4),
        "median": round(float(np.median(valid)), 4),
        "std": round(float(np.std(valid)), 4),
        "min": round(float(np.min(valid)), 4),
        "max": round(float(np.max(valid)), 4),
        "p25": round(float(np.percentile(valid, 25)), 4),
        "p75": round(float(np.percentile(valid, 75)), 4),
    }


def analyze_ndvi_trend(
    multi_year_ndvi: dict[int, np.ndarray],
) -> pd.DataFrame:
    """Analyze temporal trajectory of mean/median NDVI across multiple years."""
    records = []
    for year, ndvi_grid in sorted(multi_year_ndvi.items()):
        stats = calculate_ndvi_summary_statistics(ndvi_grid)
        stats["year"] = year
        records.append(stats)
    return pd.DataFrame(records)


def detect_vegetation_decline_hotspots(
    ndvi_earlier: np.ndarray,
    ndvi_recent: np.ndarray,
    decline_threshold: float = -0.15,
    minimum_earlier_greenness: float = 0.35,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Identify potential vegetation decline areas between two comparable seasonal windows.

    A decline hotspot is defined as a location where:
    1. The earlier NDVI was green (>= minimum_earlier_greenness, ensuring it was vegetated).
    2. Delta NDVI (recent - earlier) <= decline_threshold (statistically significant browning/loss).

    Returns:
        (delta_ndvi_grid, decline_hotspot_mask, summary_metrics)
    """
    delta_ndvi = ndvi_recent - ndvi_earlier

    # Mask locations that were originally vegetated and experienced drop
    was_vegetated = ndvi_earlier >= minimum_earlier_greenness
    decline_mask = (was_vegetated & (delta_ndvi <= decline_threshold)).astype(np.uint8)

    total_valid = np.sum(~np.isnan(delta_ndvi))
    decline_pixels = int(np.sum(decline_mask))
    decline_pct = (decline_pixels / total_valid) * 100.0 if total_valid > 0 else 0.0

    summary = {
        "decline_threshold": decline_threshold,
        "minimum_earlier_greenness": minimum_earlier_greenness,
        "total_pixels_evaluated": int(total_valid),
        "decline_hotspot_pixels": decline_pixels,
        "decline_area_pct": round(decline_pct, 3),
        "mean_delta_ndvi": round(float(np.nanmean(delta_ndvi)), 4),
    }
    return delta_ndvi, decline_mask, summary
