"""Phase 0 data-availability audit for Azamgarh District.

Run from the repo root:
    python -m src.data.data_audit
or:
    python src/data/data_audit.py

Every number comes live from Earth Engine; nothing is cached or hard-coded.
Outputs CSVs + audit_summary.md in the folder set by `output_dir` in config.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import sys
from pathlib import Path

# Ensure project root in sys.path
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import ee
import pandas as pd
import yaml

from src.data.gee_init import EarthEngineAuthError, EarthEngineConfigError, init_ee

S2_SR = "COPERNICUS/S2_SR_HARMONIZED"
CS_PLUS = "GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED"
DW = "GOOGLE/DYNAMICWORLD/V1"
LANDSAT = {
    "Landsat7_ETM+": "LANDSAT/LE07/C02/T1_L2",
    "Landsat8_OLI": "LANDSAT/LC08/C02/T1_L2",
    "Landsat9_OLI2": "LANDSAT/LC09/C02/T1_L2",
}


def load_cfg(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _find_key(props: list[str], options: list[str]) -> str | None:
    low = {p.lower(): p for p in props}
    for o in options:
        if o in low:
            return low[o]
    return None


def _ms_to_date(ms: int | float | None) -> str | None:
    if ms is None:
        return None
    return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------- boundary
def get_boundary(cfg: dict) -> tuple[ee.Geometry, list[dict]]:
    """Return (ee.Geometry, report_rows). Reports every configured dataset."""
    state = cfg["study_area"]["state"]
    district = cfg["study_area"]["district"]
    rows: list[dict] = []
    chosen: ee.Geometry | None = None

    for ds in cfg["study_area"]["boundary_datasets"]:
        try:
            fc = ee.FeatureCollection(ds)
            props = fc.first().propertyNames().getInfo()
            k1 = _find_key(props, ["adm1_name", "gaul1_name", "shapeName"])
            k2 = _find_key(props, ["adm2_name", "gaul2_name", "shapeName"])
            if not (k1 and k2):
                rows.append({"dataset": ds, "status": f"ADM1/ADM2 name properties not found; properties={props}"})
                continue
            in_state = fc.filter(ee.Filter.eq(k1, state))
            hit = in_state.filter(ee.Filter.eq(k2, district))
            n = hit.size().getInfo()
            if n == 0:
                names = sorted(set(in_state.aggregate_array(k2).getInfo()))
                close = difflib.get_close_matches(district, names, n=5, cutoff=0.5)
                rows.append({
                    "dataset": ds,
                    "status": f"NO match for '{district}' in '{state}' ({len(names)} districts). Closest: {close}",
                })
                continue
            geom = hit.geometry()
            area_km2 = geom.area(maxError=10).divide(1e6).getInfo()
            ring = geom.bounds().coordinates().getInfo()[0]
            lons, lats = [p[0] for p in ring], [p[1] for p in ring]
            rows.append({
                "dataset": ds,
                "status": "OK",
                "features": n,
                "area_km2": round(area_km2, 1),
                "bbox_lon": f"{min(lons):.3f}..{max(lons):.3f}",
                "bbox_lat": f"{min(lats):.3f}..{max(lats):.3f}",
            })
            if chosen is None:
                chosen = geom
        except Exception as e:
            rows.append({"dataset": ds, "status": f"error: {e}"})

    if chosen is None:
        print(pd.DataFrame(rows).to_string(index=False))
        raise SystemExit("No boundary dataset matched. Fix config/settings.yaml (state/district spelling).")
    return chosen, rows


# ---------------------------------------------------------------- Sentinel-2
def s2_window(region: ee.Geometry, year: int, season: dict, cfg_a: dict) -> dict:
    start = f"{year}-{season['start']}"
    end_excl = (dt.date.fromisoformat(f"{year}-{season['end']}") + dt.timedelta(days=1)).isoformat()
    s2 = ee.ImageCollection(S2_SR).filterBounds(region).filterDate(start, end_excl)

    head = ee.Dictionary({
        "scenes": s2.size(),
        "dates": ee.List(s2.aggregate_array("system:time_start"))
                   .map(lambda t: ee.Date(t).format("YYYY-MM-dd")).distinct().size(),
        "tiles": s2.aggregate_array("MGRS_TILE").distinct(),
        "mean_cloudy_pct": s2.aggregate_mean("CLOUDY_PIXEL_PERCENTAGE"),
    }).getInfo()

    out = {
        "window": f"{start}..{season['end']}",
        "scenes": head["scenes"],
        "dates": head["dates"],
        "tiles": ",".join(head["tiles"] or []),
        "mean_cloudy_pct": None if head["mean_cloudy_pct"] is None else round(head["mean_cloudy_pct"], 1),
        "mean_clear_obs": None,
        "frac_geN": None,
    }
    if head["scenes"] == 0:
        return out

    cs = ee.ImageCollection(CS_PLUS).filterBounds(region).filterDate(start, end_excl)
    joined = ee.Join.saveFirst("cs").apply(
        primary=s2,
        secondary=cs,
        condition=ee.Filter.equals(leftField="system:index", rightField="system:index"),
    )

    def _clear_mask(img):
        cs_img = ee.Image(img.get("cs"))
        return cs_img.select("cs_cdf").gte(cfg_a["cloud_score_threshold"]).rename("clear")

    clear_stack = ee.ImageCollection(joined).map(_clear_mask)
    clear_count = clear_stack.sum().clip(region)

    stats = clear_count.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            reducer2=ee.Reducer.frequencyHistogram(), sharedInputs=True
        ),
        geometry=region,
        scale=cfg_a["coverage_scale_m"],
        maxPixels=1e8,
        bestEffort=True,
    ).getInfo()

    out["mean_clear_obs"] = round(stats.get("clear_mean", 0.0) or 0.0, 2)
    hist = stats.get("clear_histogram") or {}
    total = sum(hist.values())
    geN = sum(cnt for k, cnt in hist.items() if float(k) >= cfg_a["min_valid_obs"])
    out["frac_geN"] = round(geN / total, 3) if total else 0.0
    return out


# ---------------------------------------------------------------- helpers
def date_range(collection_id: str, region: ee.Geometry) -> dict:
    c = ee.ImageCollection(collection_id).filterBounds(region)
    n = c.size().getInfo()
    if n == 0:
        return {"scenes_over_aoi": 0, "first_date": None, "last_date": None}
    earliest = c.sort("system:time_start", True).first().get("system:time_start").getInfo()
    latest = c.sort("system:time_start", False).first().get("system:time_start").getInfo()
    return {"scenes_over_aoi": n, "first_date": _ms_to_date(earliest), "last_date": _ms_to_date(latest)}


def yearly_counts(collection_id: str, region: ee.Geometry, years: list[int], cloud_prop: str | None = None, cloud_max: float | None = None) -> list[dict]:
    out = []
    base = ee.ImageCollection(collection_id).filterBounds(region)
    for y in years:
        sub = base.filterDate(f"{y}-01-01", f"{y + 1}-01-01")
        row = {"year": y, "scenes": sub.size().getInfo()}
        if cloud_prop and cloud_max is not None:
            row["low_cloud_scenes"] = sub.filter(ee.Filter.lte(cloud_prop, cloud_max)).size().getInfo()
        out.append(row)
    return out


def flag(frac: float | None, cfg_a: dict) -> str:
    if frac is None:
        return "NONE"
    if frac >= cfg_a["flag_good"]:
        return "GOOD"
    if frac >= cfg_a["flag_partial"]:
        return "PARTIAL"
    return "POOR"


# ---------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description="Audit satellite data availability for Azamgarh.")
    ap.add_argument("--config", default="config/settings.yaml")
    args = ap.parse_args()
    cfg = load_cfg(args.config)
    a = cfg["audit"]
    out_dir = Path(cfg["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        project = init_ee(raise_exit=False)
    except (EarthEngineAuthError, EarthEngineConfigError) as err:
        sys.stderr.write(f"\n[ERROR] Earth Engine initialization failed:\n{err}\n")
        sys.exit(1)

    print(f"Earth Engine OK | project={project} | earthengine-api={ee.__version__}\n")

    print("== 1. Boundary check ==")
    region, brow = get_boundary(cfg)
    bdf = pd.DataFrame(brow)
    print(bdf.to_string(index=False), "\n")
    bdf.to_csv(out_dir / "boundary_report.csv", index=False)

    print("== 2. Collection date ranges over the district ==")
    ranges = {
        name: date_range(cid, region)
        for name, cid in {"S2_SR_HARMONIZED": S2_SR, "DynamicWorld": DW, **LANDSAT}.items()
    }
    rdf = pd.DataFrame(ranges).T
    print(rdf.to_string(), "\n")
    rdf.to_csv(out_dir / "collection_ranges.csv")

    print("== 3. Sentinel-2 SR: year x season (this is the multi-window step) ==")
    rows = []
    for y in a["years"]:
        for sname, swin in a["seasons"].items():
            try:
                r = s2_window(region, y, swin, a)
                r.update({"year": y, "season": sname})
                r["flag"] = flag(r["frac_geN"], a)
            except Exception as e:
                r = {"year": y, "season": sname, "flag": "ERROR", "error": str(e)}
            rows.append(r)
            print(f"  {y} {sname:12s} scenes={r.get('scenes')} fracN={r.get('frac_geN')} -> {r['flag']}")
    s2df = pd.DataFrame(rows)
    s2df.to_csv(out_dir / "s2_year_season_audit.csv", index=False)

    print("\n== 4. Landsat Collection 2 L2 (yearly) ==")
    ls_rows = []
    for name, cid in LANDSAT.items():
        for r in yearly_counts(cid, region, a["years"], "CLOUD_COVER", a["landsat_cloud_max"]):
            r["sensor"] = name
            ls_rows.append(r)
    lsdf = pd.DataFrame(ls_rows)[["sensor", "year", "scenes", "low_cloud_scenes"]]
    print(lsdf.to_string(index=False))
    lsdf.to_csv(out_dir / "landsat_yearly.csv", index=False)

    print("\n== 5. Dynamic World scene counts (yearly) ==")
    dwdf = pd.DataFrame(yearly_counts(DW, region, a["years"]))[["year", "scenes"]]
    print(dwdf.to_string(index=False))
    dwdf.to_csv(out_dir / "dynamicworld_yearly.csv", index=False)

    # Summary markdown
    ok = s2df[s2df["flag"].isin(["GOOD", "PARTIAL"])]
    pivot = s2df.pivot(index="year", columns="season", values="flag")
    utc_now_str = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
    md = [
        f"# Azamgarh Phase 0 audit\n\nRun (UTC): {utc_now_str} | earthengine-api {ee.__version__}\n",
        "## Boundary\n",
        bdf.to_markdown(index=False) if hasattr(bdf, "to_markdown") else bdf.to_string(index=False),
        "\n\n## S2 flags (year x season)\n",
        "```\n" + pivot.to_string() + "\n```",
        f"\n\nHeuristic flags: GOOD >= {a['flag_good']:.0%} of pixels with >= {a['min_valid_obs']} clear obs "
        f"(Cloud Score+ >= {a['cloud_score_threshold']}); PARTIAL >= {a['flag_partial']:.0%}. "
        "Thresholds are our own choice, not a published standard.\n",
        f"Year-season windows with GOOD/PARTIAL: {len(ok)} of {len(s2df)}.\n",
    ]
    (out_dir / "audit_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nSaved results to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
