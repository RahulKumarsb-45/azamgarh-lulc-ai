# Technical Audit Findings & Remediation Report

**Project Title:** AI-Based Land Use/Land Cover (LULC) Classification, Change Detection, and Future Prediction for Azamgarh District, Uttar Pradesh, India  
**Audit Date:** October 21, 2026  
**Auditor:** Senior Geospatial AI Engineer, Remote Sensing Researcher & QA Architect  
**Project Workspace:** `c:\Users\kumar\Desktop\azamgarh-lulc`  
**Python Runtime:** Python 3.12.7 (Windows x64)

---

## 1. Executive Summary

A comprehensive, ground-up technical, scientific, and software engineering audit was conducted across every file, module, configuration, test suite, dashboard page, and documentation artifact in the Azamgarh LULC project repository. 

Rather than relying on claims in existing markdown summaries or test logs, every component was independently inspected and executed in the local Python 3.12 environment. Multiple genuine bugs, scientific discrepancies, and software defects were identified, diagnosed, remediated, and verified with newly authored regression tests.

All 39 automated tests (38 offline unit/integration/smoke tests and 1 live Earth Engine connectivity test) now execute cleanly: **38 PASSED, 1 SKIPPED (live EE test skipped as designed in offline mode), 0 FAILED**.

---

## 2. Confirmed Issues & Applied Fixes

### Issue 1: `pytest.ini` UTF-8 Byte-Order Mark (BOM) Crash
- **Severity:** Critical (Blocks entire test execution)
- **Root Cause:** `pytest.ini` was encoded as UTF-8 with BOM (`\ufeff[pytest]`). The `iniconfig` parser used by pytest failed on line 1 with `ERROR: pytest.ini:1: unexpected line: '\ufeff[pytest]'`, preventing any test collection or execution.
- **Remediation:** Rewrote `pytest.ini` as clean ASCII / standard UTF-8 without BOM.
- **Verification:** `pytest` collected and executed all test suites without startup errors.

### Issue 2: Streamlit Dashboard Page 6 Runtime Crash (`KeyError: 'class_metrics'`)
- **Severity:** High (Crash in user-facing web dashboard)
- **Root Cause:** When `accuracy_metrics.json` was loaded by `data_loader.py:load_validation_metrics()`, it only contained top-level scalar metrics and raw confusion matrices. In `dashboard/pages/page6_accuracy.py`, line 86 attempted direct indexing `cm_df = eval_dict["class_metrics"]`, raising an unhandled `KeyError` and crashing Page 6.
- **Remediation:**
  1. Updated `src/pipeline.py` to serialize `class_metrics` as a list of records into `accuracy_metrics.json`.
  2. Updated `dashboard/data_loader.py` to automatically detect and load `data/outputs/metrics/class_validation_metrics.csv` as a DataFrame attached to the metrics dictionary.
  3. Hardened `dashboard/pages/page6_accuracy.py` with multi-tier fallbacks (DataFrame check, list of dicts, CSV read, and on-the-fly confusion matrix computation).
- **Verification:** Added `test_all_dashboard_page_renders()` to `tests/test_dashboard_smoke.py`, which directly executes all 7 dashboard render functions and confirms zero crashes.

### Issue 3: Misrepresentation of Synthetic Data as Satellite Data in Dashboard
- **Severity:** High (Scientific integrity / Academic compliance)
- **Root Cause:** In `dashboard/data_loader.py`, lines 113 and 125 hardcoded `"is_synthetic": False` for any file loaded from `data/outputs/classified/` or `data/outputs/predictions/`. Consequently, when the offline pipeline generated synthetic demonstration rasters, the dashboard displayed them as `(Sentinel-2 L2A Classified)` instead of `(Synthetic Test Fixture)`, and suppressed demo disclaimers.
- **Remediation:**
  1. Added `is_demo_mode()` to `dashboard/data_loader.py` that verifies `data/outputs/provenance.json` and `accuracy_metrics.json`.
  2. Dynamically set `"is_synthetic": is_demo_mode()` for all loaded raster maps.
  3. Added clear, styled warning banners across all 7 dashboard pages:
     `⚠️ DEMO / SYNTHETIC DATA — NOT VALIDATED SATELLITE RESULTS`
     notifying users that the outputs are offline demonstration fixtures and authentic results require GEE authentication.
- **Verification:** Tested dashboard pages and verified `is_demo_mode()` returns `True` and warning banners render correctly.

### Issue 4: Olofsson et al. (2014) Area-Adjusted Accuracy Unexecuted in Pipeline
- **Severity:** Medium (Methodological gap)
- **Root Cause:** `compute_olofsson_adjusted_areas` was imported in `src/pipeline.py` but never called in `run_offline_synthetic_pipeline()`. The documented `91.84%` area-adjusted accuracy was hardcoded in reports without reproducible calculation. Furthermore, `compute_olofsson_adjusted_areas` assumed the input matrix had rows as map classes, whereas scikit-learn's `confusion_matrix(y_true, y_pred)` outputs reference classes as rows.
- **Remediation:**
  1. Added `matrix_orientation` argument (`"map_rows"` or `"ref_rows"`) to `compute_olofsson_adjusted_areas` in `src/models/validation.py`. When `"ref_rows"`, it transposes the matrix to align with Olofsson strata.
  2. Integrated `compute_olofsson_adjusted_areas` into step 4 of `src/pipeline.py`, using the mapped 2025 class area proportions.
  3. Exported `data/outputs/metrics/olofsson_adjusted_areas.csv` with adjusted areas, standard errors, and 95% confidence intervals.
  4. Embedded `area_adjusted_accuracy_pct` into `accuracy_metrics.json` and `provenance.json`.
- **Verification:** Unit test `test_olofsson_ref_rows_orientation` verified that adjusted cropland area equals mapped area ($2,752.26\text{ km}^2$), total adjusted area equals total study area ($4,054.0\text{ km}^2$), and standard errors compute safely.

### Issue 5: Numerical Discrepancy in Cropland-to-Built-up Conversion Claims
- **Severity:** Medium (Documentation / Academic accuracy)
- **Root Cause:** Documentation (`docs/project_report.md`, `docs/viva_qa_guide.md`, `docs/presentation_outline.md`, and `FINAL_AUDIT.md`) repeatedly cited **18.40 km² (1,840 ha)** of cropland converted to built-up land. However, the actual reproducible synthetic raster ($100 \times 100$ grid over $4,054\text{ km}^2$) had 414 transition pixels, equating to **167.84 km² (16,784 ha)** (4.14% of the landscape).
- **Remediation:** Reconciled all documentation to cite the exact verified conversion numbers ($167.84\text{ km}^2$ / $16,784\text{ ha}$ in the $100 \times 100$ synthetic raster), explicitly explaining that this is a simulated trajectory and that authentic hectarage will be derived from live Sentinel-2 imagery.
- **Verification:** Confirmed exact match between `data/outputs/change/critical_transitions_2019_2025.csv`, `class_area_summary.csv`, and documentation.

### Issue 6: Incomplete Dashboard Smoke Testing
- **Severity:** Medium (QA gap)
- **Root Cause:** `tests/test_dashboard_smoke.py` only checked `assert callable(render_overview_page)`. None of the page render functions were actually called, allowing the Page 6 `KeyError` to slip through unnoticed.
- **Remediation:** Added `test_all_dashboard_page_renders()` to `test_dashboard_smoke.py` which executes `render_overview_page()`, `render_maps_page()`, `render_change_page()`, `render_vegetation_page()`, `render_prediction_page()`, `render_accuracy_page()`, and `render_downloads_page()`.
- **Verification:** Test now executes all render logic and passes in pytest.

### Issue 7: Figure of Merit (FoM) vs Spatial Agreement Interpretation Gap
- **Severity:** Low (Scientific interpretation)
- **Root Cause:** Historical backtesting yielded **95.72%** spatial agreement alongside **0.0161 (1.61%)** Figure of Merit. Without academic explanation, reviewers or viva examiners might misinterpret the high spatial agreement as proof of perfect forecasting while overlooking the low FoM.
- **Remediation:** Clarified in `docs/prediction_methodology.md`, `docs/project_report.md`, `README.md`, and dashboard Page 5 that the 95.72% agreement is largely driven by landscape persistence (~95% unchanged pixels), whereas Figure of Merit (Pontius et al. 2008) measures allocation accuracy strictly on changed pixels ($1.61\%$).
- **Verification:** Documented in report, README, and interactive dashboard banner.

---

## 3. Data Integrity & Provenance Classification

To strictly avoid scientific ambiguity, all project datasets and outputs are categorized into two explicit tiers:

| Tier | Directory | Description | Validation Status |
|---|---|---|---|
| **Tier 1: Synthetic Test Fixtures** | `data/synthetic_fixture/` | Mathematical fixtures generated for offline unit testing, algorithm validation, and schema testing. | **VERIFIED OFFLINE** |
| **Tier 2: Pipeline Outputs (Offline Mode)** | `data/outputs/` | Outputs generated by running `python src/pipeline.py --mode synthetic`. Tagged with `is_synthetic: true` in `provenance.json`. | **VERIFIED OFFLINE** |
| **Tier 3: Authentic Satellite Data** | `data/outputs/` (Live mode) | Generated when user executes `python src/pipeline.py --mode live` with active GCP Earth Engine credentials. | **PENDING USER GEE AUTH** |

---

## 4. Summary of Test Suite Execution

```
Platform: Windows (Python 3.12.7, pytest-8.3.4, pluggy-1.6.0)
Root Directory: c:\Users\kumar\Desktop\azamgarh-lulc
Test Command: pytest -v

tests/test_area_stats.py::test_calculate_class_areas_conservation_and_hectares PASSED
tests/test_area_stats.py::test_calculate_gain_loss PASSED
tests/test_change_detection.py::test_detect_land_cover_changes PASSED
tests/test_change_detection.py::test_extract_critical_transitions PASSED
tests/test_change_detection.py::test_identify_change_hotspots PASSED
tests/test_config.py::test_settings_yaml_structure PASSED
tests/test_config.py::test_class_schema_yaml_integrity PASSED
tests/test_config.py::test_dynamic_world_reference_mapping PASSED
tests/test_dashboard_smoke.py::test_dashboard_imports_and_components PASSED
tests/test_dashboard_smoke.py::test_data_loader_fallbacks PASSED
tests/test_dashboard_smoke.py::test_all_dashboard_page_renders PASSED
tests/test_dashboard_smoke.py::test_demo_mode_detection PASSED
tests/test_error_handling.py::test_gee_init_missing_or_invalid_project PASSED
tests/test_error_handling.py::test_classifier_predict_before_fit PASSED
tests/test_error_handling.py::test_calculate_class_areas_invalid_input PASSED
tests/test_error_handling.py::test_export_geotiff_invalid_shape PASSED
tests/test_exports.py::test_export_csv_summary PASSED
tests/test_exports.py::test_export_metadata_json PASSED
tests/test_exports.py::test_generate_publication_map_figure PASSED
tests/test_geotiff_export.py::test_export_geotiff_georeferencing PASSED
tests/test_geotiff_export.py::test_export_geotiff_utm_projection PASSED
tests/test_indices.py::test_safe_normalized_difference_division_by_zero PASSED
tests/test_indices.py::test_calculate_ndvi PASSED
tests/test_indices.py::test_calculate_mndwi PASSED
tests/test_indices.py::test_calculate_indices_dataframe PASSED
tests/test_indices.py::test_seasonal_metrics PASSED
tests/test_live_ee.py::test_live_earth_engine_connectivity SKIPPED (live_ee requires GCP auth)
tests/test_pipeline_integration.py::test_offline_pipeline_sandbox_execution PASSED
tests/test_prediction.py::test_transition_probability_row_stochastic PASSED
tests/test_prediction.py::test_markov_prediction_conservation PASSED
tests/test_prediction.py::test_cellular_automata_markov_simulation PASSED
tests/test_prediction.py::test_run_historical_backtest PASSED
tests/test_samples.py::test_spatial_blocks_creation PASSED
tests/test_samples.py::test_spatial_block_zero_leakage_split PASSED
tests/test_samples.py::test_compute_inter_rater_agreement PASSED
tests/test_validation.py::test_evaluate_classification_perfect PASSED
tests/test_validation.py::test_evaluate_classification_with_errors PASSED
tests/test_validation.py::test_olofsson_area_adjusted_accuracy PASSED
tests/test_validation.py::test_olofsson_ref_rows_orientation PASSED

======================== 38 passed, 1 skipped in 9.72s ========================
```
