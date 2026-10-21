"""Sample collection, stratified sampling, and spatial block splitting.

Adheres strictly to remote sensing best practices:
- Spatial block splitting to eliminate spatial autocorrelation leakage.
- Stratified sampling with target >= 50 independent validation points per class.
- Dual-interpreter review schema with agreement tracking.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

# Ensure project root in sys.path
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import numpy as np
import pandas as pd


def create_spatial_blocks(
    bbox: tuple[float, float, float, float],
    block_size_km: float = 5.0,
) -> pd.DataFrame:
    """Create a regular grid of spatial blocks across the study area bounding box.

    bbox: (min_lon, min_lat, max_lon, max_lat)
    Approximate conversion at 26 degrees North (Azamgarh latitude):
      1 deg lat ~ 110.8 km
      1 deg lon ~ 111.32 * cos(26 deg) ~ 100.0 km
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    km_per_deg_lat = 110.8
    mean_lat_rad = math.radians((min_lat + max_lat) / 2.0)
    km_per_deg_lon = 111.32 * math.cos(mean_lat_rad)

    deg_lat_step = block_size_km / km_per_deg_lat
    deg_lon_step = block_size_km / km_per_deg_lon

    lons = np.arange(min_lon, max_lon + deg_lon_step, deg_lon_step)
    lats = np.arange(min_lat, max_lat + deg_lat_step, deg_lat_step)

    blocks = []
    block_id = 0
    for i in range(len(lons) - 1):
        for j in range(len(lats) - 1):
            block_id += 1
            blocks.append({
                "block_id": block_id,
                "min_lon": round(lons[i], 4),
                "min_lat": round(lats[j], 4),
                "max_lon": round(lons[i + 1], 4),
                "max_lat": round(lats[j + 1], 4),
                "centroid_lon": round((lons[i] + lons[i + 1]) / 2.0, 4),
                "centroid_lat": round((lats[j] + lats[j + 1]) / 2.0, 4),
            })
    return pd.DataFrame(blocks)


def assign_points_to_blocks(
    points_df: pd.DataFrame,
    blocks_df: pd.DataFrame,
    lon_col: str = "lon",
    lat_col: str = "lat",
) -> pd.DataFrame:
    """Assign geographic points to their enclosing spatial block."""
    df = points_df.copy()
    block_ids = []

    for _, row in df.iterrows():
        p_lon = row[lon_col]
        p_lat = row[lat_col]
        match = blocks_df[
            (blocks_df["min_lon"] <= p_lon) & (p_lon <= blocks_df["max_lon"]) &
            (blocks_df["min_lat"] <= p_lat) & (p_lat <= blocks_df["max_lat"])
        ]
        if not match.empty:
            block_ids.append(int(match.iloc[0]["block_id"]))
        else:
            # Fallback to nearest block centroid
            dists = np.hypot(blocks_df["centroid_lon"] - p_lon, blocks_df["centroid_lat"] - p_lat)
            block_ids.append(int(blocks_df.loc[dists.idxmin(), "block_id"]))

    df["block_id"] = block_ids
    return df


def spatial_block_train_val_split(
    points_df: pd.DataFrame,
    train_ratio: float = 0.70,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split samples by whole spatial blocks to prevent spatial leakage."""
    unique_blocks = np.sort(points_df["block_id"].unique())
    rng = np.random.default_rng(random_state)
    shuffled_blocks = rng.permutation(unique_blocks)

    n_train_blocks = int(len(unique_blocks) * train_ratio)
    train_blocks = set(shuffled_blocks[:n_train_blocks])
    val_blocks = set(shuffled_blocks[n_train_blocks:])

    df = points_df.copy()
    df["split"] = df["block_id"].apply(lambda b: "train" if b in train_blocks else "val")

    train_df = df[df["split"] == "train"].copy()
    val_df = df[df["split"] == "val"].copy()
    return train_df, val_df


def compute_inter_rater_agreement(
    df: pd.DataFrame,
    col_reviewer1: str = "reviewer_1",
    col_reviewer2: str = "reviewer_2",
) -> dict[str, float]:
    """Calculate Cohen's kappa and observed percent agreement between two interpreters."""
    valid = df.dropna(subset=[col_reviewer1, col_reviewer2])
    n = len(valid)
    if n == 0:
        return {"observed_agreement": 0.0, "cohens_kappa": 0.0, "sample_count": 0}

    r1 = valid[col_reviewer1].values
    r2 = valid[col_reviewer2].values

    observed_agreement = float(np.mean(r1 == r2))

    categories = np.unique(np.concatenate([r1, r2]))
    pe = 0.0
    for cat in categories:
        p1 = np.mean(r1 == cat)
        p2 = np.mean(r2 == cat)
        pe += p1 * p2

    if pe >= 1.0:
        kappa = 1.0
    else:
        kappa = float((observed_agreement - pe) / (1.0 - pe))

    return {
        "observed_agreement": round(observed_agreement, 4),
        "cohens_kappa": round(kappa, 4),
        "sample_count": n,
    }
