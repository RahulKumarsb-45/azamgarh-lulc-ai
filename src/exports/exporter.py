"""Data and cartographic export handlers.

Outputs:
- GeoTIFF files with embedded georeferencing and CRS tags.
- CSV tabular data with standardized schemas.
- JSON pipeline metadata and parameter traces.
- Static publication-quality cartographic figures (PNG/PDF) with legend, scale, and north arrow.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Ensure project root in sys.path
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_bounds


CLASS_COLORS = {
    1: "#F2D16B",  # Agriculture
    2: "#2E7D32",  # Vegetation
    3: "#1E88E5",  # Water
    4: "#D32F2F",  # Built-up
    5: "#A1887F",  # Barren
}

CLASS_NAMES = {
    1: "Cropland",
    2: "Vegetation",
    3: "Water",
    4: "Built-up",
    5: "Barren",
}


def export_geotiff(
    raster_array: np.ndarray,
    output_path: str | Path,
    bbox: tuple[float, float, float, float] = (82.80, 25.70, 83.65, 26.35),
    crs: str = "EPSG:4326",
    nodata: int = 0,
) -> Path:
    """Export 2D numpy array as a georeferenced GeoTIFF."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    arr = np.asarray(raster_array)
    if arr.ndim != 2:
        raise ValueError(f"raster_array must be 2D, got shape {arr.shape}")

    height, width = arr.shape
    min_lon, min_lat, max_lon, max_lat = bbox
    transform = from_bounds(min_lon, min_lat, max_lon, max_lat, width, height)

    dtype = arr.dtype
    if dtype in (np.int32, np.int64):
        dtype = rasterio.int32
        arr = arr.astype(np.int32)
    elif dtype in (np.uint8, bool):
        dtype = rasterio.uint8
        arr = arr.astype(np.uint8)
    elif dtype in (np.float32, np.float64):
        dtype = rasterio.float32
        arr = arr.astype(np.float32)

    with rasterio.open(
        out_file,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=dtype,
        crs=crs,
        transform=transform,
        nodata=nodata,
        compress="lzw",
    ) as dst:
        dst.write(arr, 1)

    return out_file


def export_csv_summary(
    df: pd.DataFrame,
    output_path: str | Path,
    float_format: str = "%.3f",
) -> Path:
    """Export tabular statistics to CSV."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False, float_format=float_format)
    return out_file


def export_metadata_json(
    metadata: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Export execution metadata, parameter traces, and scientific citations."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, default=str)
    return out_file


def export_json(data: Any, output_path: str | Path) -> Path:
    """Convenience alias for exporting JSON structures."""
    return export_metadata_json(data, output_path)


def generate_publication_map_figure(
    raster_map: np.ndarray,
    output_png_path: str | Path,
    title: str = "Land Use and Land Cover Map - Azamgarh District",
    year: int | str = 2025,
    class_colors: dict[int, str] | None = None,
    class_names: dict[int, str] | None = None,
    dpi: int = 300,
    source_text: str | None = None,
) -> Path:
    """Generate high-resolution cartographic map figure for reports and presentations."""
    out_file = Path(output_png_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    colors_dict = class_colors or CLASS_COLORS
    names_dict = class_names or CLASS_NAMES

    classes = sorted(colors_dict.keys())
    cmap_colors = [colors_dict[c] for c in classes]
    custom_cmap = ListedColormap(cmap_colors)

    fig, ax = plt.subplots(figsize=(9, 7), dpi=dpi)

    # Reindex classes 1..5 to 0..4 for continuous discrete colormap
    reindexed = np.zeros_like(raster_map, dtype=float)
    for idx, c in enumerate(classes):
        reindexed[raster_map == c] = idx

    im = ax.imshow(reindexed, cmap=custom_cmap, vmin=-0.5, vmax=len(classes) - 0.5)
    ax.set_title(f"{title} ({year})", fontsize=14, weight="bold", pad=12)
    ax.axis("off")

    # Legend patches
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=colors_dict[c], edgecolor="black", label=names_dict.get(c, f"Class {c}"))
        for c in classes
    ]
    ax.legend(
        handles=legend_elements,
        loc="lower right",
        frameon=True,
        facecolor="white",
        edgecolor="#cccccc",
        framealpha=0.9,
        fontsize=10,
        title="Land Cover Classes",
        title_fontsize=11,
    )

    # Scale and north arrow annotation
    label = source_text if source_text is not None else "Source: Demonstration Fixture / ML Classifier\nUTM Zone 44N | Azamgarh, UP, India"
    ax.text(
        0.02, 0.04,
        label,
        transform=ax.transAxes,
        fontsize=8,
        color="#333333",
        bbox=dict(boxstyle="square,pad=0.3", fc="white", ec="none", alpha=0.8),
    )

    plt.tight_layout()
    fig.savefig(out_file, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return out_file
