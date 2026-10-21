"""Land cover change detection, critical transition tracking, and hotspot mapping.

Detects:
- Pixel-by-pixel transitions across years.
- Urban expansion over fertile cropland (Cropland -> Built-up).
- Vegetation loss and gain dynamics.
- Spatial change hotspots using kernel density estimation.
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


DEFAULT_CLASS_NAMES = {
    1: "Agriculture / Cropland",
    2: "Vegetation",
    3: "Water Bodies",
    4: "Built-up Areas",
    5: "Barren / Open Land",
}


def detect_land_cover_changes(
    map_t1: np.ndarray,
    map_t2: np.ndarray,
    classes: list[int] | None = None,
    class_names: dict[int, str] | None = None,
) -> tuple[np.ndarray, pd.DataFrame]:
    """Compute binary and categorical change raster and cross-tabulation table."""
    classes = classes or sorted(DEFAULT_CLASS_NAMES.keys())
    names = class_names or DEFAULT_CLASS_NAMES

    y1 = np.asarray(map_t1)
    y2 = np.asarray(map_t2)

    if y1.shape != y2.shape:
        raise ValueError(f"Input rasters must have identical spatial dimensions; got {y1.shape} and {y2.shape}")

    # Binary change map (1 = changed, 0 = unchanged)
    changed_mask = (y1 != y2).astype(np.uint8)

    # Cross-tabulation of pixel transitions
    transitions = []
    total_pixels = y1.size

    for c1 in classes:
        for c2 in classes:
            count = int(np.sum((y1 == c1) & (y2 == c2)))
            pct = (count / total_pixels) * 100.0
            transitions.append({
                "from_code": int(c1),
                "from_name": names.get(c1, str(c1)),
                "to_code": int(c2),
                "to_name": names.get(c2, str(c2)),
                "transition_label": f"{names.get(c1, str(c1))} -> {names.get(c2, str(c2))}",
                "pixel_count": count,
                "pct_of_landscape": round(pct, 3),
                "is_change": bool(c1 != c2),
            })

    trans_df = pd.DataFrame(transitions)
    return changed_mask, trans_df


def extract_critical_transitions(
    trans_df: pd.DataFrame,
    pixel_size_m: float = 20.0,
    total_reference_area_km2: float | None = 4054.0,
) -> pd.DataFrame:
    """Filter and highlight high-priority socio-ecological transitions in km² and ha."""
    changes = trans_df[trans_df["is_change"]].copy()

    if total_reference_area_km2 is not None:
        total_p = trans_df["pixel_count"].sum()
        changes["estimated_area_km2"] = round(
            (changes["pixel_count"] / total_p) * total_reference_area_km2, 2
        )
    else:
        pixel_area_km2 = (pixel_size_m * pixel_size_m) / 1e6
        changes["estimated_area_km2"] = round(changes["pixel_count"] * pixel_area_km2, 2)

    changes["estimated_area_ha"] = round(changes["estimated_area_km2"] * 100.0, 2)
    changes = changes.sort_values(by="pixel_count", ascending=False)
    return changes


def identify_change_hotspots(
    change_mask: np.ndarray,
    kernel_size: int = 15,
    hotspot_threshold_pct: float = 25.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute local change density to delineate spatial change hotspots.

    Returns:
        (density_grid, hotspot_binary_mask)
    """
    kernel = np.ones((kernel_size, kernel_size), dtype=float)
    kernel_area = kernel.size
    kernel /= kernel_area

    density = convolve2d(change_mask.astype(float), kernel, mode="same", boundary="symm")
    density_pct = density * 100.0

    hotspot_mask = (density_pct >= hotspot_threshold_pct).astype(np.uint8)
    return density_pct, hotspot_mask
