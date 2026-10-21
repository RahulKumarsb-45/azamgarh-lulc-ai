# Unit Test Instructions & Execution Results

This document records the automated verification suite, test coverage, and verification results for the Azamgarh LULC engineering pipeline.

---

## 1. Running the Automated Test Suite

Execute pytest from the repository root:
```powershell
.\.venv\Scripts\Activate.ps1
pytest -v
```

To run with full stdout print statements:
```powershell
pytest -v -s
```

---

## 2. Test Suite Architecture

| Test Module | Coverage Scope | Critical Scientific Checks |
|---|---|---|
| `tests/test_indices.py` | Spectral index calculations | NDVI, NDWI (McFeeters), NDBI formulas; zero-denominator protection; phenological swing metric. |
| `tests/test_samples.py` | Spatial partitioning | Spatial grid block generation; **Zero-leakage assertion** (`train_blocks.isdisjoint(val_blocks)`); inter-rater Cohen's kappa. |
| `tests/test_validation.py` | Error matrix & metrics | Confusion matrix diagonals; OA, PA (Recall), UA (Precision), F1-Score; Olofsson (2014) area-adjusted estimation. |
| `tests/test_area_stats.py` | Area statistics | Percentage sums strictly to 100.0%; area in km² conservation; gain/loss accounting. |
| `tests/test_prediction.py` | Predictive modeling | Row-stochasticity ($\sum_j P_{ij} = 1.0$); total area conservation in Markov projections; CA-Markov 2D spatial simulation; historical backtesting metrics. |
| `tests/test_dashboard_smoke.py` | Interactive dashboard | Import integrity across all 7 Streamlit pages; data loader fallback resilience. |

---

## 3. Actual Test Execution Log

**Execution Date:** 2026-10-21  
**Environment:** Windows 11 (64-bit), Python 3.12.7, pytest 9.1.1, pluggy 1.7.0  
**Command:** `.\.venv\Scripts\pytest.exe -v`

```
============================= test session starts =============================
platform win32 -- Python 3.12.7, pytest-9.1.1, pluggy-1.7.0 -- .venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\kumar\Desktop\azamgarh-lulc
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 18 items

tests/test_area_stats.py::test_calculate_class_areas PASSED              [  5%]
tests/test_area_stats.py::test_calculate_gain_loss PASSED                [ 11%]
tests/test_dashboard_smoke.py::test_dashboard_imports_and_components PASSED [ 16%]
tests/test_dashboard_smoke.py::test_data_loader_fallbacks PASSED         [ 22%]
tests/test_indices.py::test_safe_normalized_difference PASSED            [ 27%]
tests/test_indices.py::test_calculate_ndvi PASSED                        [ 33%]
tests/test_indices.py::test_calculate_indices_dataframe PASSED           [ 38%]
tests/test_indices.py::test_seasonal_metrics PASSED                      [ 44%]
tests/test_prediction.py::test_transition_probability_row_stochastic PASSED [ 50%]
tests/test_prediction.py::test_markov_prediction_conservation PASSED     [ 55%]
tests/test_prediction.py::test_cellular_automata_markov_simulation PASSED [ 61%]
tests/test_prediction.py::test_run_historical_backtest PASSED            [ 66%]
tests/test_samples.py::test_spatial_blocks_creation PASSED               [ 72%]
tests/test_samples.py::test_spatial_block_zero_leakage_split PASSED      [ 77%]
tests/test_samples.py::test_compute_inter_rater_agreement PASSED         [ 83%]
tests/test_validation.py::test_evaluate_classification_perfect PASSED    [ 88%]
tests/test_validation.py::test_evaluate_classification_with_errors PASSED [ 94%]
tests/test_validation.py::test_olofsson_area_adjusted_accuracy PASSED    [100%]

============================= 18 passed in 4.67s ==============================
```

**Result:** 100% of unit and integration tests passed cleanly.
