# Comparative Audit: Archive vs. Verified Workspace

**Target Archive:** `azamgarh-lulc-audited-final.zip`  
**Deliverable Archive:** `azamgarh-lulc-verified-release.zip`  
**Audit Date:** October 21, 2026  
**Auditor:** Senior Geospatial AI Engineer & Project Release Engineer  

---

## 1. Archive Structure and Packaging Comparison

| Metric / Aspect | `azamgarh-lulc-audited-final.zip` | `azamgarh-lulc-verified-release.zip` (Deliverable) | Status / Action Taken |
|---|---|---|---|
| **Root Archive Layout** | Encapsulated in nested root folder (`azamgarh-lulc/...`) | Clean direct root structure (`src/`, `dashboard/`, `data/`, etc.) | **Fixed:** Removed redundant root folder wrapper |
| **Nested ZIP Files** | None inside archive | None inside archive (`*.zip` strictly excluded) | **Verified:** Release rule strictly enforced |
| **Cache & Temp Files** | Clean (no `__pycache__` or `.pytest_cache`) | Clean (no `__pycache__` or `.pytest_cache`) | **Verified:** Excluded from build |
| **Credentials & Secrets** | Clean (`.env.example` only, no `.env` or tokens) | Clean (`.env.example` only, no `.env` or tokens) | **Verified:** Zero credential leakage |
| **Total Tracked Files** | 105 files | 107 files (including audit reports & expanded tests) | **Enhanced** |

---

## 2. Comparative File Status Matrix Summary

From `docs/comparative_file_matrix.csv`:
- **Identical Files (97):** All baseline source codes, dashboard pages, synthetic test fixtures, and documentation preserved byte-for-byte.
- **Modified Files in Verified Workspace (8):**
  1. `config/settings.yaml`: Added `MNDWI` to the `classification.indices` list to maintain 100% configuration alignment with the Random Forest feature pipeline.
  2. `src/analysis/change_detection.py`: Added explicit spatial dimension validation (`if y1.shape != y2.shape`) with informative error messaging before matrix operations.
  3. `tests/test_area_stats.py`: Added `test_calculate_class_areas_raw_pixel_mode` and `test_summarize_multi_year_areas` covering multi-year aggregation.
  4. `tests/test_error_handling.py`: Added `test_detect_land_cover_changes_mismatched_shapes` testing dimension mismatch rejection.
  5. `tests/test_exports.py`: Added `test_export_json_alias` verifying export convenience wrapper.
  6. `tests/test_indices.py`: Added explicit unit tests for `calculate_ndwi` and `calculate_ndbi`.
  7. `tests/test_prediction.py`: Added `test_transition_probability_zero_changes` verifying identity transition stability.
  8. `tests/test_validation.py`: Added `test_olofsson_zero_sample_stratum_handling` verifying safe variance estimation when a stratum contains zero or one sample.
- **New Files (2):**
  - `docs/comparative_audit.md` (this report)
  - `docs/comparative_file_matrix.csv` (SHA-256 comparative matrix)

---

## 3. Test Suite Expansion

| Test File | Previous Tests | Current Verified Tests | New Coverage Area |
|---|---|---|---|
| `test_area_stats.py` | 2 | 4 | Raw pixel metric area mode & multi-year summary table |
| `test_change_detection.py` | 3 | 3 | Categorical transitions, critical shifts, and 2D convolution |
| `test_config.py` | 3 | 3 | YAML configuration integrity, 5-class schema, and Dynamic World mapping |
| `test_dashboard_smoke.py` | 4 | 4 | All 7 Streamlit render functions & demo mode detection |
| `test_error_handling.py` | 4 | 5 | Mismatched raster shape validation for change detection |
| `test_exports.py` | 3 | 4 | JSON convenience export wrapper |
| `test_geotiff_export.py` | 2 | 2 | GeoTIFF affine transform, CRS EPSG:4326/32644, NoData |
| `test_indices.py` | 5 | 7 | Direct NDWI and NDBI formula unit checks |
| `test_live_ee.py` | 1 (skipped offline) | 1 (skipped offline) | Live Earth Engine connectivity marker |
| `test_pipeline_integration.py` | 1 | 1 | End-to-end sandbox execution in isolated temp directory |
| `test_prediction.py` | 4 | 5 | Unchanged / zero-transition identity matrix stability |
| `test_samples.py` | 3 | 3 | 5 km spatial blocks, zero-leakage split, and dual-rater Kappa |
| `test_validation.py` | 4 | 5 | Zero-sample stratum edge case in Olofsson standard error |
| **Total** | **39 (38 pass, 1 skip)** | **47 (46 pass, 1 skip)** | **Comprehensive invariant and edge-case coverage** |

---

## 4. Verification Verdict

The verified workspace retains 100% backward compatibility with all previously audited pipeline outputs while eliminating configuration discrepancies, hardening raster input checks, and strengthening automated test coverage.
