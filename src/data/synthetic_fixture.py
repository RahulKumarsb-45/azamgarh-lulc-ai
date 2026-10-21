"""Synthetic test fixture generator for offline testing of calculations and pipeline.

IMPORTANT DISCLAIMER:
This module generates SYNTHETIC TEST FIXTURES strictly for unit testing,
algorithm verification, and demonstration when Earth Engine authentication is pending.
These outputs are explicitly flagged as synthetic and MUST NEVER be reported as real
satellite observations of Azamgarh District.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root in sys.path
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import numpy as np
import pandas as pd
import yaml

from src.features.indices import calculate_indices


def generate_synthetic_study_area(
    bbox: tuple[float, float, float, float] = (82.80, 25.70, 83.65, 26.35),
    grid_size: int = 100,
    seed: int = 42,
) -> dict:
    """Generate a 2D synthetic spatial grid over the approximate bbox of Azamgarh."""
    rng = np.random.default_rng(seed)
    min_lon, min_lat, max_lon, max_lat = bbox

    lons = np.linspace(min_lon, max_lon, grid_size)
    lats = np.linspace(max_lat, min_lat, grid_size)

    # Underlying spatial landscape:
    # Dominant class 1 (Cropland ~ 75%)
    # Class 2 (Vegetation ~ 10%)
    # Class 3 (Water ~ 2% - e.g. Tamsa River meander)
    # Class 4 (Built-up ~ 10% - Azamgarh city & rural settlements)
    # Class 5 (Barren / Open ~ 3%)
    class_grid_2019 = np.ones((grid_size, grid_size), dtype=np.int32)

    # Settlement clusters (Azamgarh city and tehsils)
    centers = [
        (grid_size // 2, grid_size // 2),
        (grid_size // 4, 3 * grid_size // 4),
        (3 * grid_size // 4, grid_size // 3),
    ]
    for cy, cx in centers:
        y, x = np.ogrid[:grid_size, :grid_size]
        dist = np.hypot(y - cy, x - cx)
        class_grid_2019[dist < grid_size * 0.12] = 4

    # River feature (Class 3: Water)
    for c in range(grid_size):
        r = int(grid_size * 0.45 + np.sin(c / 8.0) * (grid_size * 0.08))
        if 0 <= r < grid_size:
            class_grid_2019[max(0, r - 1):min(grid_size, r + 2), c] = 3

    # Vegetation patches along river & orchards (Class 2: Vegetation)
    veg_mask = rng.random((grid_size, grid_size)) < 0.12
    class_grid_2019[(class_grid_2019 == 1) & veg_mask] = 2

    # Barren / open patches (Class 5)
    barren_mask = rng.random((grid_size, grid_size)) < 0.03
    class_grid_2019[(class_grid_2019 == 1) & barren_mask] = 5

    # Realistic transition from 2019 -> 2022 -> 2025:
    # Ongoing urbanization: small conversion from Cropland/Barren -> Built-up
    class_grid_2022 = class_grid_2019.copy()
    urban_expansion_2022 = (rng.random((grid_size, grid_size)) < 0.03) & (class_grid_2019 == 1)
    class_grid_2022[urban_expansion_2022] = 4

    class_grid_2025 = class_grid_2022.copy()
    urban_expansion_2025 = (rng.random((grid_size, grid_size)) < 0.03) & (class_grid_2022 == 1)
    class_grid_2025[urban_expansion_2025] = 4

    return {
        "lons": lons,
        "lats": lats,
        "bbox": bbox,
        "grid_size": grid_size,
        "maps": {
            2019: class_grid_2019,
            2022: class_grid_2022,
            2025: class_grid_2025,
        },
        "is_synthetic": True,
        "disclaimer": "SYNTHETIC TEST FIXTURE ONLY - NOT OBSERVED SATELLITE DATA",
    }


def generate_synthetic_spectral_samples(
    n_samples_per_class: int = 150,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate realistic synthetic Sentinel-2 surface reflectance bands for each class."""
    rng = np.random.default_rng(seed)
    records = []

    # Reflectance profiles (mean, std) for Sentinel-2 bands: [B2, B3, B4, B8, B11, B12]
    profiles = {
        1: {  # Cropland
            "name": "Agriculture / Cropland",
            "means": [0.06, 0.09, 0.08, 0.38, 0.18, 0.11],
            "stds":  [0.015, 0.02, 0.02, 0.05, 0.03, 0.02],
        },
        2: {  # Perennial Vegetation
            "name": "Vegetation",
            "means": [0.03, 0.06, 0.04, 0.45, 0.14, 0.07],
            "stds":  [0.01, 0.015, 0.015, 0.04, 0.02, 0.015],
        },
        3: {  # Water Bodies
            "name": "Water Bodies",
            "means": [0.08, 0.09, 0.05, 0.02, 0.01, 0.01],
            "stds":  [0.02, 0.02, 0.015, 0.01, 0.005, 0.005],
        },
        4: {  # Built-up
            "name": "Built-up Areas",
            "means": [0.12, 0.14, 0.16, 0.22, 0.28, 0.22],
            "stds":  [0.025, 0.025, 0.03, 0.03, 0.04, 0.03],
        },
        5: {  # Barren / Open
            "name": "Barren / Open Land",
            "means": [0.14, 0.18, 0.22, 0.26, 0.34, 0.28],
            "stds":  [0.03, 0.03, 0.035, 0.035, 0.04, 0.035],
        },
    }

    bbox = (82.80, 25.70, 83.65, 26.35)
    sample_id = 0

    for class_code, p in profiles.items():
        for _ in range(n_samples_per_class):
            sample_id += 1
            bands = rng.normal(p["means"], p["stds"])
            bands = np.clip(bands, 0.001, 0.999)

            # Assign random geographic coordinate inside bounding box
            lon = rng.uniform(bbox[0], bbox[2])
            lat = rng.uniform(bbox[1], bbox[3])

            records.append({
                "sample_id": sample_id,
                "lon": round(lon, 5),
                "lat": round(lat, 5),
                "class_code": class_code,
                "class_name": p["name"],
                "B2": round(float(bands[0]), 4),
                "B3": round(float(bands[1]), 4),
                "B4": round(float(bands[2]), 4),
                "B8": round(float(bands[3]), 4),
                "B11": round(float(bands[4]), 4),
                "B12": round(float(bands[5]), 4),
                "reviewer_1": class_code,
                # Simulate realistic 95% inter-rater agreement for reviewer 2
                "reviewer_2": class_code if rng.random() > 0.05 else int(rng.choice([c for c in profiles if c != class_code])),
                "confidence": "high",
                "is_synthetic": True,
            })

    df = pd.DataFrame(records)
    # Compute spectral indices (NDVI, NDWI, MNDWI, NDBI)
    df = calculate_indices(df)
    return df


def save_synthetic_fixtures(output_dir: str = "data/synthetic_fixture") -> Path:
    """Save generated synthetic test fixtures to disk for testing pipelines."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    samples_df = generate_synthetic_spectral_samples()
    samples_path = out / "synthetic_reference_samples.csv"
    samples_df.to_csv(samples_path, index=False)

    spatial_fixture = generate_synthetic_study_area()
    meta = {
        "is_synthetic": True,
        "disclaimer": spatial_fixture["disclaimer"],
        "bbox": spatial_fixture["bbox"],
        "grid_size": spatial_fixture["grid_size"],
        "years": list(spatial_fixture["maps"].keys()),
    }
    with open(out / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    for year, grid in spatial_fixture["maps"].items():
        np.save(out / f"synthetic_map_{year}.npy", grid)

    return out


if __name__ == "__main__":
    p = save_synthetic_fixtures()
    print(f"Synthetic fixtures saved to {p.resolve()}")
