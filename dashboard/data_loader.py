"""Data loader and cache manager for the Streamlit dashboard.

Separates data fetching from rendering, provides robust caching, and handles
missing or synthetic files gracefully without crashing.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st
import yaml


CLASS_COLORS = {
    1: "#F2D16B",  # Agriculture / Cropland
    2: "#2E7D32",  # Vegetation
    3: "#1E88E5",  # Water Bodies
    4: "#D32F2F",  # Built-up Areas
    5: "#A1887F",  # Barren / Open Land
}

CLASS_NAMES = {
    1: "Agriculture / Cropland",
    2: "Vegetation",
    3: "Water Bodies",
    4: "Built-up Areas",
    5: "Barren / Open Land",
}


@st.cache_data
def load_class_schema() -> dict:
    """Load class schema configuration."""
    path = Path("config/class_schema.yaml")
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {"classes": {k: {"name": v, "color": CLASS_COLORS[k]} for k, v in CLASS_NAMES.items()}}


@st.cache_data
def load_settings() -> dict:
    """Load settings configuration."""
    path = Path("config/settings.yaml")
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


@st.cache_data
def load_audit_data() -> dict[str, Any]:
    """Load Phase 0 audit outputs if generated."""
    audit_dir = Path("data/outputs/audit")
    out = {
        "is_available": False,
        "boundary": None,
        "collection_ranges": None,
        "s2_audit": None,
        "landsat": None,
        "dynamic_world": None,
        "summary_md": "",
    }
    if not audit_dir.exists():
        return out

    b_file = audit_dir / "boundary_report.csv"
    if b_file.is_file():
        out["boundary"] = pd.read_csv(b_file)
        out["is_available"] = True

    c_file = audit_dir / "collection_ranges.csv"
    if c_file.is_file():
        out["collection_ranges"] = pd.read_csv(c_file)

    s2_file = audit_dir / "s2_year_season_audit.csv"
    if s2_file.is_file():
        out["s2_audit"] = pd.read_csv(s2_file)

    ls_file = audit_dir / "landsat_yearly.csv"
    if ls_file.is_file():
        out["landsat"] = pd.read_csv(ls_file)

    dw_file = audit_dir / "dynamicworld_yearly.csv"
    if dw_file.is_file():
        out["dynamic_world"] = pd.read_csv(dw_file)

    md_file = audit_dir / "audit_summary.md"
    if md_file.is_file():
        out["summary_md"] = md_file.read_text(encoding="utf-8")

    return out


@st.cache_data
def is_demo_mode() -> bool:
    """Check if system is operating in synthetic / demo mode."""
    prov_file = Path("data/outputs/provenance.json")
    if prov_file.is_file():
        try:
            with open(prov_file, "r", encoding="utf-8") as f:
                prov = json.load(f)
                return bool(prov.get("is_synthetic", True))
        except Exception:
            pass

    metrics_file = Path("data/outputs/metrics/accuracy_metrics.json")
    if metrics_file.is_file():
        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("is_synthetic", True))
        except Exception:
            pass
    return True


@st.cache_data
def load_available_raster_maps() -> dict[int | str, dict]:
    """Load classified raster maps (real or synthetic fallback) with accurate provenance tagging."""
    maps: dict[int | str, dict] = {}
    is_syn = is_demo_mode()

    # Check real outputs first
    real_dir = Path("data/outputs/classified")
    if real_dir.exists():
        for f in sorted(real_dir.glob("*.npy")):
            try:
                # Name pattern: lulc_map_2025.npy
                year_part = f.stem.split("_")[-1]
                year = int(year_part) if year_part.isdigit() else year_part
                data = np.load(f)
                maps[year] = {"data": data, "is_synthetic": is_syn, "source": f.name}
            except Exception:
                continue

    # Also check predictions
    pred_dir = Path("data/outputs/predictions")
    if pred_dir.exists():
        for f in sorted(pred_dir.glob("*.npy")):
            try:
                year_part = f.stem.split("_")[-1]
                year = int(year_part) if year_part.isdigit() else year_part
                data = np.load(f)
                maps[year] = {"data": data, "is_synthetic": is_syn, "source": f.name}
            except Exception:
                continue

    # Fallback to synthetic test fixtures if real outputs not yet generated
    if not maps:
        syn_dir = Path("data/synthetic_fixture")
        if syn_dir.exists():
            for f in sorted(syn_dir.glob("synthetic_map_*.npy")):
                try:
                    year_part = f.stem.split("_")[-1]
                    year = int(year_part) if year_part.isdigit() else year_part
                    data = np.load(f)
                    maps[year] = {"data": data, "is_synthetic": True, "source": f.name}
                except Exception:
                    continue

    return maps


@st.cache_data
def load_area_statistics() -> pd.DataFrame | None:
    """Load computed area statistics CSV if available."""
    candidates = [
        Path("data/outputs/change/class_area_summary.csv"),
        Path("data/outputs/classified/area_summary.csv"),
        Path("data/synthetic_fixture/synthetic_area_summary.csv"),
    ]
    for c in candidates:
        if c.is_file():
            return pd.read_csv(c)
    return None


@st.cache_data
def load_validation_metrics() -> dict | None:
    """Load model accuracy and validation metrics, attaching tabular class metrics."""
    candidates = [
        Path("data/outputs/metrics/accuracy_metrics.json"),
        Path("data/synthetic_fixture/synthetic_accuracy_metrics.json"),
    ]
    metrics = None
    for c in candidates:
        if c.is_file():
            try:
                with open(c, "r", encoding="utf-8") as f:
                    metrics = json.load(f)
                break
            except Exception:
                continue

    if metrics is None:
        return None

    # Attach per-class metrics DataFrame if available
    class_metrics_csv = Path("data/outputs/metrics/class_validation_metrics.csv")
    if class_metrics_csv.is_file():
        metrics["class_metrics"] = pd.read_csv(class_metrics_csv)
    elif "class_metrics" in metrics and isinstance(metrics["class_metrics"], list):
        metrics["class_metrics"] = pd.DataFrame(metrics["class_metrics"])

    # Attach Olofsson area-adjusted DataFrame if available
    olofsson_csv = Path("data/outputs/metrics/olofsson_adjusted_areas.csv")
    if olofsson_csv.is_file():
        metrics["olofsson_adjusted"] = pd.read_csv(olofsson_csv)

    return metrics


@st.cache_data
def load_backtest_results() -> dict | None:
    """Load historical backtest evaluation results."""
    candidates = [
        Path("data/outputs/metrics/backtest_results.json"),
        Path("data/synthetic_fixture/synthetic_backtest_results.json"),
    ]
    for c in candidates:
        if c.is_file():
            try:
                with open(c, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                continue
    return None
