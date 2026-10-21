"""Land cover area statistics and gain/loss calculation.

Computes exact class areas in square kilometres and hectares, as well as percentage shares.
Maintains rigorous scientific accounting:
- Total percentage sums strictly to 100%.
- Pixel area is calculated from spatial resolution (e.g. 20 m x 20 m = 400 m² = 0.0004 km² = 0.04 ha).
- Gain, loss, and net change accounting across historical and predicted years.
- 1 km² = 100 hectares (ha).
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


DEFAULT_CLASS_NAMES = {
    1: "Agriculture / Cropland",
    2: "Vegetation",
    3: "Water Bodies",
    4: "Built-up Areas",
    5: "Barren / Open Land",
}


def calculate_class_areas(
    classification_map: np.ndarray,
    pixel_size_m: float = 20.0,
    total_reference_area_km2: float | None = None,
    classes: list[int] | None = None,
    class_names: dict[int, str] | None = None,
) -> pd.DataFrame:
    """Calculate class-wise area in km², hectares, and percentage for a raster map.

    If total_reference_area_km2 is provided (e.g. official district area 4054.0 km²),
    percentages are mapped strictly to that baseline.
    """
    classes = classes or sorted(DEFAULT_CLASS_NAMES.keys())
    names = class_names or DEFAULT_CLASS_NAMES

    flat = classification_map.flatten()
    valid_mask = np.isin(flat, classes)
    valid_pixels = flat[valid_mask]
    total_valid_count = len(valid_pixels)

    if total_valid_count == 0:
        raise ValueError("Classification map contains zero valid pixels matching class schema.")

    pixel_area_km2 = (pixel_size_m * pixel_size_m) / 1e6

    records = []
    for c in classes:
        n_pixels = int(np.sum(valid_pixels == c))
        pct = (n_pixels / total_valid_count) * 100.0

        if total_reference_area_km2 is not None:
            area_km2 = (pct / 100.0) * total_reference_area_km2
        else:
            area_km2 = n_pixels * pixel_area_km2

        area_ha = area_km2 * 100.0  # 1 km² = 100 hectares

        records.append({
            "class_code": c,
            "class_name": names.get(c, f"Class {c}"),
            "pixel_count": n_pixels,
            "area_km2": round(area_km2, 2),
            "area_ha": round(area_ha, 2),
            "percentage": round(pct, 2),
        })

    df = pd.DataFrame(records)
    return df


def calculate_gain_loss(
    area_df_t1: pd.DataFrame,
    area_df_t2: pd.DataFrame,
    year_t1: int,
    year_t2: int,
) -> pd.DataFrame:
    """Compute absolute change (km² and hectares), percentage point change, and relative change (%) per class."""
    m = pd.merge(
        area_df_t1[["class_code", "class_name", "area_km2", "area_ha", "percentage"]],
        area_df_t2[["class_code", "area_km2", "area_ha", "percentage"]],
        on="class_code",
        suffixes=(f"_{year_t1}", f"_{year_t2}"),
    )

    m["abs_change_km2"] = round(m[f"area_km2_{year_t2}"] - m[f"area_km2_{year_t1}"], 2)
    m["abs_change_ha"] = round(m["abs_change_km2"] * 100.0, 2)
    m["pct_pt_change"] = round(m[f"percentage_{year_t2}"] - m[f"percentage_{year_t1}"], 2)

    # Relative percentage change: ((A2 - A1) / A1) * 100
    eps = 1e-4
    m["relative_change_pct"] = round(
        ((m[f"area_km2_{year_t2}"] - m[f"area_km2_{year_t1}"]) / (m[f"area_km2_{year_t1}"] + eps)) * 100.0,
        2,
    )

    m["trend"] = m["abs_change_km2"].apply(
        lambda x: "Expansion" if x > 0.05 else ("Decline" if x < -0.05 else "Stable")
    )
    return m


def summarize_multi_year_areas(
    yearly_maps: dict[int, np.ndarray],
    pixel_size_m: float = 20.0,
    total_reference_area_km2: float | None = 4054.0,
    classes: list[int] | None = None,
    class_names: dict[int, str] | None = None,
) -> pd.DataFrame:
    """Summarize class area trajectories across multiple years into a single consolidated table."""
    all_rows = []
    for year, m in sorted(yearly_maps.items()):
        df = calculate_class_areas(
            m,
            pixel_size_m=pixel_size_m,
            total_reference_area_km2=total_reference_area_km2,
            classes=classes,
            class_names=class_names,
        )
        df["year"] = year
        all_rows.append(df)
    return pd.concat(all_rows, ignore_index=True)
