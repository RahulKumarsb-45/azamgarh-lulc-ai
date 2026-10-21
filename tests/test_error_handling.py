"""Unit tests for error handling: missing .env, invalid EE_PROJECT, unfitted models, invalid inputs."""
import os
from pathlib import Path
import numpy as np
import pytest

from src.analysis.area_stats import calculate_class_areas
from src.data.gee_init import EarthEngineConfigError, init_ee
from src.exports.exporter import export_geotiff
from src.models.classifier import LULCRandomForestClassifier


def test_gee_init_missing_or_invalid_project(monkeypatch):
    # Simulate missing EE_PROJECT
    monkeypatch.setenv("EE_PROJECT", "")
    with pytest.raises(EarthEngineConfigError):
        init_ee(raise_exit=False)

    # Simulate placeholder EE_PROJECT
    monkeypatch.setenv("EE_PROJECT", "your-gcp-project-id")
    with pytest.raises(EarthEngineConfigError):
        init_ee(raise_exit=False)


def test_classifier_predict_before_fit():
    clf = LULCRandomForestClassifier()
    with pytest.raises(RuntimeError, match="must be fitted before predict"):
        clf.predict(np.zeros((5, 9)))

    with pytest.raises(RuntimeError, match="must be fitted before predict_proba"):
        clf.predict_proba(np.zeros((5, 9)))

    with pytest.raises(RuntimeError, match="must be fitted first"):
        clf.get_feature_importances()


def test_calculate_class_areas_invalid_input():
    # Array with no valid classes (e.g. all zeros or 999)
    bad_map = np.full((10, 10), 999, dtype=np.int32)
    with pytest.raises(ValueError, match="zero valid pixels"):
        calculate_class_areas(bad_map)


def test_export_geotiff_invalid_shape(tmp_path: Path):
    bad_arr = np.zeros((5, 5, 5))
    with pytest.raises(ValueError, match="must be 2D"):
        export_geotiff(bad_arr, tmp_path / "fail.tif")


def test_detect_land_cover_changes_mismatched_shapes():
    from src.analysis.change_detection import detect_land_cover_changes
    m1 = np.ones((10, 10), dtype=np.int32)
    m2 = np.ones((10, 12), dtype=np.int32)
    with pytest.raises(ValueError, match="identical spatial dimensions"):
        detect_land_cover_changes(m1, m2)

