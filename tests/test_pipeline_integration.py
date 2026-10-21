"""Integration test for offline verification pipeline using a temporary output sandbox."""
from pathlib import Path
import pytest
import yaml

from src.pipeline import run_offline_synthetic_pipeline


def test_offline_pipeline_sandbox_execution(tmp_path: Path):
    # Load base configuration
    base_cfg_path = Path("config/settings.yaml")
    cfg = yaml.safe_load(base_cfg_path.read_text(encoding="utf-8"))

    # Redirect all output paths to tmp_path sandbox
    sandbox_dir = tmp_path / "sandbox_outputs"
    cfg["paths"]["output_dir"] = str(sandbox_dir)
    cfg["paths"]["classified_maps_dir"] = str(sandbox_dir / "classified")
    cfg["paths"]["change_analysis_dir"] = str(sandbox_dir / "change")
    cfg["paths"]["predictions_dir"] = str(sandbox_dir / "predictions")
    cfg["paths"]["metrics_dir"] = str(sandbox_dir / "metrics")
    cfg["paths"]["figures_dir"] = str(sandbox_dir / "figures")

    # Fast parameters for test
    cfg["classification"]["rf_params"]["n_estimators"] = 10
    cfg["classification"]["rf_params"]["max_depth"] = 4

    temp_cfg_path = tmp_path / "test_settings.yaml"
    temp_cfg_path.write_text(yaml.dump(cfg), encoding="utf-8")

    # Run pipeline pointing strictly to temporary configuration
    run_offline_synthetic_pipeline(cfg_path=str(temp_cfg_path))

    # Assert outputs were generated in the sandbox
    assert (sandbox_dir / "classified" / "lulc_map_2019.tif").is_file()
    assert (sandbox_dir / "classified" / "lulc_map_2022.tif").is_file()
    assert (sandbox_dir / "classified" / "lulc_map_2025.tif").is_file()
    assert (sandbox_dir / "change" / "class_area_summary.csv").is_file()
    assert (sandbox_dir / "change" / "critical_transitions_2019_2025.csv").is_file()
    assert (sandbox_dir / "predictions" / "predicted_map_2030.tif").is_file()
    assert (sandbox_dir / "predictions" / "predicted_map_2035.tif").is_file()
    assert (sandbox_dir / "metrics" / "accuracy_metrics.json").is_file()
    assert (sandbox_dir / "metrics" / "olofsson_adjusted_areas.csv").is_file()
    assert (sandbox_dir / "metrics" / "backtest_results.json").is_file()
    assert (sandbox_dir / "figures" / "map_figure_2025.png").is_file()
    assert (sandbox_dir / "provenance.json").is_file()

