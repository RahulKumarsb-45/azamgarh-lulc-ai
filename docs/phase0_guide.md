# Phase 0 Guide: Azamgarh LULC

Status legend: **[verified]** = checked in official catalog docs today; **[to verify]** = you must confirm via the audit; **[our choice]** = design decision, not a standard.

## A. Feasibility (short)
- Free data + free GEE (noncommercial/research) = feasible for a 2-person minor project.
- Biggest risk: **consistent historical maps**. Sentinel-2 SR in Earth Engine starts 2017-03-28, but 2017-2018 L2A coverage is not global yet [verified]. So 2016-2018 may be thin or missing for Azamgarh [to verify via audit].
- Monsoon (Jul-Sep) clouds will hurt kharif mapping [to verify via audit]. We therefore also audit a post-monsoon window.
- Labels: no ground truth exists for past years. You must create validation samples by visual interpretation. This is the most time-consuming task.

## B. Historical range (provisional, decide after audit)
1. **Core series (Sentinel-2, 10 m):** start from the first year where the audit shows GOOD/PARTIAL in rabi AND (zaid or kharif_post). Likely 2019 -> 2025 [to verify].
2. **Do not mix sensors inside one change statistic.** If you want 2016-2018, build a *separate* Landsat 8 (30 m) series or resample S2 to 30 m for a cross-sensor comparison, and say so in the report.
3. **MVP (Phase 1):** two years, e.g. first good year and 2025.
4. Years with insufficient imagery are reported as gaps, not interpolated.

## C. Dataset IDs
| Purpose | Earth Engine ID | Notes |
|---|---|---|
| Sentinel-2 L2A | `COPERNICUS/S2_SR_HARMONIZED` | from 2017-03-28 [verified]; 2017-18 not global |
| Sentinel-2 TOA (fallback) | `COPERNICUS/S2_HARMONIZED` | from 2015-06-27 [verified]; TOA != SR, do not mix silently |
| Cloud masking | `GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED` | band `cs_cdf` |
| Dynamic World | `GOOGLE/DYNAMICWORLD/V1` | model output, reference only |
| Landsat 7/8/9 L2 | `LANDSAT/LE07/C02/T1_L2`, `LANDSAT/LC08/C02/T1_L2`, `LANDSAT/LC09/C02/T1_L2` | [to verify via audit] |
| Boundary | `FAO/GAUL/2015/level2`, `FAO/GAUL/2025/level2` | 2015 version: non-commercial license [verified]; GAUL carries a disclaimer; cross-check area vs official district area |

Docs: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED and the same path pattern for the other IDs.

Band choices for Phase 1 (our choice): S2 `B2,B3,B4,B8,B11,B12` (+ `B5-B7,B8A` optional), SR scale 1/10000. NDVI=(B8-B4)/(B8+B4), NDWI(McFeeters)=(B3-B8)/(B3+B8), NDBI=(B11-B8)/(B11+B8). Index comparison in Phase 2, not assumed.

## D. Earth Engine registration + auth
1. Use a Google account you own (not a shared one).
2. Go to https://code.earthengine.google.com/register (if redirected, follow "Cloud project setup" in the EE docs).
3. Choose **Noncommercial / research / education**, create or select a **Google Cloud project**, note its **Project ID** (not the display name).
4. Make sure the **Earth Engine API** is enabled for that project.
5. Python needs a Cloud project even for free use: `ee.Authenticate()` then `ee.Initialize(project='...')` [verified in EE auth docs].
6. In the repo: copy `.env.example` -> `.env`, set `EE_PROJECT=<your project id>`.
7. First run opens a browser login; the token is stored locally in your user profile, never in the repo. Never share tokens/keys; `.gitignore` already blocks `.env` and credential-like files.

## E. Windows setup (PowerShell)
```powershell
# 1. Python 3.11 recommended (3.10-3.12 should work)
py -3.11 --version

# 2. Unzip repo, then:
cd azamgarh-lulc
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
# If blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Config
copy .env.example .env
notepad .env          # set EE_PROJECT

# 4. One-time login (browser)
earthengine authenticate

# 5. Git
git init
git add .
git status            # confirm .env is NOT listed
git commit -m "Phase 0 scaffold"

# 6. After first successful run, freeze versions
pip freeze > requirements.lock.txt
```

## H. Run + interpret the audit
```powershell
python -m src.data.data_audit
```
Takes several minutes (40 S2 windows). Outputs in `data/outputs/audit/`.

| File | Look at |
|---|---|
| `boundary_report.csv` | `status=OK`, area_km2 sensible vs official district area; compare 2015 vs 2025 versions. If NO match, read "Closest" names and fix `settings.yaml` |
| `collection_ranges.csv` | first/last dates per collection over Azamgarh |
| `s2_year_season_audit.csv` | `scenes`, `dates`, `tiles` (how many MGRS tiles cover the district), `frac_geN` = share of pixels with >= N clear observations; `flag` |
| `landsat_yearly.csv` | fallback for years where S2 is POOR/NONE |
| `dynamicworld_yearly.csv` | DW availability (reference only) |
| `audit_summary.md` | year x season flag table |

Decision rule (our choice): a year is **mappable** if rabi is GOOD/PARTIAL and at least one of zaid / kharif_post is GOOD/PARTIAL. Monsoon is expected to be weak; that is a finding, not a bug.

Troubleshooting: `EE_PROJECT is not set` -> fill `.env`. `Earth Engine API has not been used...` -> enable API in Cloud console. `Computation timed out` -> raise `coverage_scale_m` (e.g. 200) in settings.

## F. Five-class schema + validation sampling
Schema: see `config/class_schema.yaml`.

Cropland vs vegetation vs fallow (our choice, to be tested):
- Cropland = large seasonal NDVI swing across rabi/zaid/kharif; fallow fields inside cropland mosaic stay Cropland.
- Vegetation = high NDVI in all seasons, low swing (groves, orchards).
- Barren = bare in **all** seasons.

Sampling strategy (our choice; see Congalton 1991 and Olofsson et al. 2014 for the principles, [to verify citations before using]):
1. **Training and validation must be spatially separate.** Split the district into blocks (e.g. 5 km grid); assign blocks to train or validate.
2. **Stratified random** points per class, minimum ~50 per class for validation (rule of thumb), more for rare classes (water, barren).
3. Label by visual interpretation of same-year imagery (S2 seasonal composites; high-res imagery where dated correctly). **Dynamic World is only used to help stratify, never as the label.**
4. Both team members label independently; compute agreement; resolve disagreements; keep notes.
5. Report area-weighted accuracy where possible, since class areas are very unequal.
6. Historical years: label per year; if a point cannot be interpreted for that year, drop it (don't guess).

## I. Checklist before Phase 1
- [ ] EE registered, `earthengine authenticate` works, audit runs end to end
- [ ] Boundary status OK; area plausible vs official district figure (source cited)
- [ ] Both boundary versions compared and one chosen with reason
- [ ] First S2 SR date over Azamgarh recorded
- [ ] Year x season table reviewed; mappable years listed; gaps listed
- [ ] Number of MGRS tiles covering the district noted
- [ ] Final year pair for MVP chosen
- [ ] Class schema agreed by both members
- [ ] Labeling method + validation split agreed
- [ ] `.env` not in git; `requirements.lock.txt` created

## Phase 0 split (2 members)
- Member 1: audit run + interpretation, boundary check, schema, sampling plan.
- Member 2: repo/environment, git hygiene, README skeleton, collect audit outputs into the shared doc.
- Together: sign-off on the checklist.
