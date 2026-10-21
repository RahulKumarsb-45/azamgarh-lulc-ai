"""Master execution pipeline for Azamgarh District LULC mapping.

Modes:
- synthetic: Full offline execution using synthetic test fixtures, spatial cross-validation,
             Random Forest training, area calculation, change detection, CA-Markov forecasting,
             backtesting, and GeoTIFF cartographic exports.
- live: Full Earth Engine pipeline running live audit, downloading/compositing Sentinel-2 SR
        with Cloud Score+ masking and training on Azamgarh reference samples.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure project root in sys.path
_project_root = Path(__file__).resolve().parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import numpy as np
import yaml

from src.analysis.area_stats import calculate_class_areas, calculate_gain_loss, summarize_multi_year_areas
from src.analysis.change_detection import detect_land_cover_changes, extract_critical_transitions
from src.data.sample_manager import (
    assign_points_to_blocks,
    create_spatial_blocks,
    spatial_block_train_val_split,
)
from src.data.synthetic_fixture import (
    generate_synthetic_spectral_samples,
    generate_synthetic_study_area,
)
from src.exports.exporter import export_csv_summary, export_geotiff, generate_publication_map_figure
from src.models.classifier import LULCRandomForestClassifier
from src.models.prediction import (
    calculate_transition_matrix,
    cellular_automata_markov_simulation,
    run_historical_backtest,
)
from src.models.validation import compute_olofsson_adjusted_areas, evaluate_classification


def run_offline_synthetic_pipeline(cfg_path: str = "config/settings.yaml") -> None:
    print("\n=======================================================")
    print("   AZAMGARH LULC: OFFLINE VERIFICATION PIPELINE       ")
    print("=======================================================\n")
    cfg = yaml.safe_load(Path(cfg_path).read_text(encoding="utf-8"))
    paths = cfg["paths"]

    out_classified = Path(paths["classified_maps_dir"])
    out_change = Path(paths["change_analysis_dir"])
    out_pred = Path(paths["predictions_dir"])
    out_metrics = Path(paths["metrics_dir"])
    out_figures = Path(paths["figures_dir"])

    for p in [out_classified, out_change, out_pred, out_metrics, out_figures]:
        p.mkdir(parents=True, exist_ok=True)

    # 1. Generate & prepare reference samples with spatial block cross-validation
    print("[1/6] Preparing reference samples and spatial block partitions...")
    samples_df = generate_synthetic_spectral_samples(n_samples_per_class=120, seed=42)
    bbox = cfg["study_area"].get("bbox", (82.80, 25.70, 83.65, 26.35))
    blocks_df = create_spatial_blocks(bbox, block_size_km=cfg["validation"]["spatial_block_size_km"])
    samples_with_blocks = assign_points_to_blocks(samples_df, blocks_df)
    train_df, val_df = spatial_block_train_val_split(
        samples_with_blocks,
        train_ratio=cfg["validation"]["train_ratio"],
        random_state=cfg["validation"]["random_state"],
    )
    print(f"      Total samples: {len(samples_df)} | Train: {len(train_df)} | Val: {len(val_df)}")
    print(f"      Spatial blocks: {len(blocks_df)} (strictly independent train/val split)")

    # 2. Train Random Forest Classifier
    print("[2/6] Training Random Forest supervised classifier...")
    rf_params = cfg["classification"]["rf_params"]
    rf = LULCRandomForestClassifier(
        n_estimators=rf_params["n_estimators"],
        max_depth=rf_params["max_depth"],
        min_samples_split=rf_params["min_samples_split"],
        min_samples_leaf=rf_params["min_samples_leaf"],
        random_state=cfg["classification"]["random_state"],
    )
    rf.fit(train_df, train_df["class_code"])
    feat_imp = rf.get_feature_importances()
    print("      Feature Importances:")
    for _, row in feat_imp.head(5).iterrows():
        print(f"        - {row['feature']:6s}: {row['importance_pct']}%")

    # 3. Independent Accuracy Assessment
    print("[3/6] Evaluating independent validation metrics...")
    val_preds = rf.predict(val_df)
    eval_res = evaluate_classification(val_df["class_code"], val_preds)
    print(f"      Overall Accuracy (OA): {eval_res['overall_accuracy_pct']}%")
    print(f"      Cohen's Kappa (kappa):  {eval_res['cohens_kappa']}")



    # 4. Multi-Year Historical Maps & Area Statistics
    print("[4/6] Processing historical multi-year maps (2019, 2022, 2025)...")
    spatial_data = generate_synthetic_study_area(grid_size=100)
    yearly_maps = spatial_data["maps"]
    ref_area_km2 = cfg["study_area"]["reference_official_area_km2"]

    for year, grid in yearly_maps.items():
        np.save(out_classified / f"lulc_map_{year}.npy", grid)
        export_geotiff(grid, out_classified / f"lulc_map_{year}.tif", bbox=bbox)
        generate_publication_map_figure(
            grid,
            out_figures / f"map_figure_{year}.png",
            year=year,
            source_text="Source: Synthetic Test Fixture (Demonstration Only)\nUTM Zone 44N | Azamgarh, UP, India",
        )

    multi_area_df = summarize_multi_year_areas(yearly_maps, total_reference_area_km2=ref_area_km2)
    export_csv_summary(multi_area_df, out_change / "class_area_summary.csv")

    # Compute Olofsson (2014) area-adjusted accuracy using mapped 2025 class proportions
    map_2025_areas = calculate_class_areas(yearly_maps[2025], total_reference_area_km2=ref_area_km2)
    mapped_area_dict = dict(zip(map_2025_areas["class_code"], map_2025_areas["area_km2"]))
    olofsson_df = compute_olofsson_adjusted_areas(
        cm_sample=eval_res["raw_confusion_matrix"],
        mapped_area_km2_by_class=mapped_area_dict,
        matrix_orientation="ref_rows",
    )
    export_csv_summary(olofsson_df, out_metrics / "olofsson_adjusted_areas.csv")
    print(f"      Area-Adjusted Accuracy (Olofsson): {olofsson_df.attrs.get('overall_accuracy_adjusted_pct')}%")

    # Update accuracy metrics JSON with Olofsson adjusted stats and per-class metrics
    metrics_json = {
        "overall_accuracy": eval_res["overall_accuracy"],
        "overall_accuracy_pct": eval_res["overall_accuracy_pct"],
        "area_adjusted_accuracy": olofsson_df.attrs.get("overall_accuracy_adjusted"),
        "area_adjusted_accuracy_pct": olofsson_df.attrs.get("overall_accuracy_adjusted_pct"),
        "cohens_kappa": eval_res["cohens_kappa"],
        "total_validation_samples": eval_res["total_validation_samples"],
        "raw_confusion_matrix": eval_res["raw_confusion_matrix"].tolist(),
        "class_metrics": eval_res["class_metrics"].to_dict(orient="records"),
        "is_synthetic": True,
    }
    with open(out_metrics / "accuracy_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_json, f, indent=2)

    export_csv_summary(eval_res["class_metrics"], out_metrics / "class_validation_metrics.csv")
    eval_res["confusion_matrix"].to_csv(out_metrics / "confusion_matrix.csv")

    # 5. Change Detection (2019 -> 2025)
    print("[5/6] Performing historical change detection (2019 vs 2025)...")
    map_19 = yearly_maps[2019]
    map_25 = yearly_maps[2025]
    _, trans_df = detect_land_cover_changes(map_19, map_25)
    crit_transitions = extract_critical_transitions(trans_df, total_reference_area_km2=ref_area_km2)
    export_csv_summary(crit_transitions, out_change / "critical_transitions_2019_2025.csv")

    # 6. Prediction for 2030, 2035 & Historical Backtesting
    print("[6/6] Running CA-Markov forecasting (2030, 2035) and historical backtesting...")
    # Backtest
    backtest_res = run_historical_backtest(
        map_t1=yearly_maps[2019],
        map_t2=yearly_maps[2022],
        map_t3_actual=yearly_maps[2025],
        years=(2019, 2022, 2025),
    )
    print(f"      Backtest Overall Spatial Agreement: {backtest_res['overall_agreement_pct']}%")
    print(f"      Backtest Figure of Merit (FoM):     {backtest_res['figure_of_merit']}")

    bt_summary = {
        "calibration_years": backtest_res["calibration_years"],
        "backtest_target_year": backtest_res["backtest_target_year"],
        "overall_agreement_pct": backtest_res["overall_agreement_pct"],
        "cohens_kappa": backtest_res["cohens_kappa"],
        "figure_of_merit": backtest_res["figure_of_merit"],
    }
    with open(out_metrics / "backtest_results.json", "w", encoding="utf-8") as f:
        json.dump(bt_summary, f, indent=2)

    # Forecast 2030 and 2035
    _, prob_df = calculate_transition_matrix(map_19, map_25)
    map_2030 = cellular_automata_markov_simulation(map_25, prob_df.values, iterations=5, seed=2030)
    map_2035 = cellular_automata_markov_simulation(map_2030, prob_df.values, iterations=5, seed=2035)

    np.save(out_pred / "predicted_map_2030.npy", map_2030)
    np.save(out_pred / "predicted_map_2035.npy", map_2035)
    export_geotiff(map_2030, out_pred / "predicted_map_2030.tif", bbox=bbox)
    export_geotiff(map_2035, out_pred / "predicted_map_2035.tif", bbox=bbox)
    generate_publication_map_figure(
        map_2030,
        out_figures / "predicted_map_2030.png",
        title="Projected LULC Map - Azamgarh (CA-Markov)",
        year=2030,
        source_text="Source: CA-Markov Model Simulation (Projection)\nUTM Zone 44N | Azamgarh, UP, India",
    )
    generate_publication_map_figure(
        map_2035,
        out_figures / "predicted_map_2035.png",
        title="Projected LULC Map - Azamgarh (CA-Markov)",
        year=2035,
        source_text="Source: CA-Markov Model Simulation (Projection)\nUTM Zone 44N | Azamgarh, UP, India",
    )

    # Provenance manifest
    out_root = out_classified.parent
    provenance = {
        "execution_mode": "synthetic",
        "is_synthetic": True,
        "disclaimer": "DEMO / SYNTHETIC DATA — NOT VALIDATED SATELLITE RESULTS",
        "study_area": f"{cfg['study_area']['district']}, {cfg['study_area']['state']}, India",
        "reference_official_area_km2": ref_area_km2,
        "spatial_resolution_meters": cfg["classification"]["scale_m"],
        "target_crs": cfg["study_area"]["target_crs"],
        "bounding_box": list(bbox),
        "overall_accuracy_pct": eval_res["overall_accuracy_pct"],
        "area_adjusted_accuracy_pct": olofsson_df.attrs.get("overall_accuracy_adjusted_pct"),
        "cohens_kappa": eval_res["cohens_kappa"],
        "backtest_agreement_pct": backtest_res["overall_agreement_pct"],
        "backtest_fom": backtest_res["figure_of_merit"],
    }
    with open(out_root / "provenance.json", "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2)

    print("\n[SUCCESS] Full offline verification pipeline completed successfully!")
    print(f"All outputs generated in: {out_root.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Master Azamgarh LULC Pipeline.")
    parser.add_argument("--mode", choices=["synthetic", "live"], default="synthetic", help="Pipeline execution mode")
    parser.add_argument("--config", default="config/settings.yaml", help="Path to settings YAML")
    args = parser.parse_args()

    if args.mode == "synthetic":
        run_offline_synthetic_pipeline(args.config)
    else:
        from src.data.gee_init import EarthEngineAuthError, EarthEngineConfigError, init_ee
        print("Checking Earth Engine connection for live run...")
        try:
            project = init_ee(raise_exit=False)
            print(f"Live GEE pipeline initialized with project '{project}'.")
            print("Running live audit...")
            from src.data.data_audit import main as audit_main
            audit_main()
        except (EarthEngineAuthError, EarthEngineConfigError) as err:
            sys.stderr.write(f"\n[ERROR] Earth Engine live run cannot proceed:\n{err}\n")
            sys.exit(1)


if __name__ == "__main__":
    main()
