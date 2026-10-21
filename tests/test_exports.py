"""Unit tests for CSV tabular exports, JSON parameter traces, and publication cartographic figures."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.exports.exporter import (
    export_csv_summary,
    export_json,
    export_metadata_json,
    generate_publication_map_figure,
)


def test_export_csv_summary(tmp_path: Path):
    df = pd.DataFrame({
        "class_code": [1, 2, 3],
        "area_km2": [3000.5, 500.2, 100.1],
        "area_ha": [300050.0, 50020.0, 10010.0],
    })
    out_csv = tmp_path / "test_summary.csv"
    res = export_csv_summary(df, out_csv)
    assert res.is_file()

    read_back = pd.read_csv(res)
    assert len(read_back) == 3
    assert "area_ha" in read_back.columns


def test_export_metadata_json(tmp_path: Path):
    meta = {
        "project": "Azamgarh LULC",
        "target_crs": "EPSG:32644",
        "accuracy": 0.9275,
        "is_synthetic": True,
    }
    out_json = tmp_path / "meta.json"
    res = export_metadata_json(meta, out_json)
    assert res.is_file()

    with open(res, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["project"] == "Azamgarh LULC"
    assert loaded["accuracy"] == 0.9275


def test_generate_publication_map_figure(tmp_path: Path):
    grid = np.array([
        [1, 1, 2, 3],
        [1, 4, 4, 2],
        [5, 4, 1, 1],
    ], dtype=np.int32)
    out_png = tmp_path / "figure.png"
    res = generate_publication_map_figure(grid, out_png, year=2025, dpi=100)
    assert res.is_file()
    assert res.stat().st_size > 5000  # valid image file with reasonable bytes


def test_export_json_alias(tmp_path: Path):
    data = {"metric": "test", "value": 42}
    out_file = tmp_path / "alias.json"
    res = export_json(data, out_file)
    assert res.is_file()
    with open(res, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["metric"] == "test"
    assert loaded["value"] == 42

