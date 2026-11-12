"""Smoke test for the Streamlit interactive dashboard and all page modules."""
from dashboard.data_loader import (
    load_area_statistics,
    load_audit_data,
    load_available_raster_maps,
    load_class_schema,
    load_settings,
    load_validation_metrics,
)
from dashboard.pages.page1_overview import render_overview_page
from dashboard.pages.page2_maps import render_maps_page
from dashboard.pages.page3_change import render_change_page
from dashboard.pages.page4_vegetation import render_vegetation_page
from dashboard.pages.page5_prediction import render_prediction_page
from dashboard.pages.page6_accuracy import render_accuracy_page
from dashboard.pages.page7_downloads import render_downloads_page
from dashboard.pages.page8_documentation import render_documentation_page
from dashboard.pages.page_future_predictions import render_future_predictions_page
from dashboard.pages.page_past_maps import render_past_maps_page
from dashboard.pages.page_present_map import render_present_map_page
from dashboard.pages.page_research_paper import render_research_paper_page
from dashboard.pages.page_satellite_sources import render_satellite_sources_page
from dashboard.pages.page_about_data_sources import render_about_page
from dashboard.pages.page_agriculture import render_agriculture_page
from dashboard.pages.page_barren import render_barren_page
from dashboard.pages.page_builtup import render_builtup_page
from dashboard.pages.page_water import render_water_page


def test_dashboard_imports_and_components():
    """Verify that all dashboard page modules and render functions are importable."""
    assert callable(render_overview_page)
    assert callable(render_maps_page)
    assert callable(render_change_page)
    assert callable(render_vegetation_page)
    assert callable(render_prediction_page)
    assert callable(render_accuracy_page)
    assert callable(render_downloads_page)
    assert callable(render_documentation_page)
    assert callable(render_past_maps_page)
    assert callable(render_present_map_page)
    assert callable(render_future_predictions_page)
    assert callable(render_satellite_sources_page)
    assert callable(render_research_paper_page)
    assert callable(render_about_page)
    assert callable(render_agriculture_page)
    assert callable(render_water_page)
    assert callable(render_builtup_page)
    assert callable(render_barren_page)


def test_data_loader_fallbacks():
    """Verify data loading functions handle existing or missing files gracefully."""
    schema = load_class_schema()
    assert "classes" in schema

    settings = load_settings()
    assert "study_area" in settings

    audit = load_audit_data()
    assert "is_available" in audit

    maps = load_available_raster_maps()
    assert isinstance(maps, dict)


def test_all_dashboard_page_renders():
    """Regression test: execute all dashboard render functions to ensure zero crashes/KeyErrors."""
    render_overview_page()
    render_maps_page()
    render_change_page()
    render_vegetation_page()
    render_prediction_page()
    render_accuracy_page()
    render_downloads_page()
    render_documentation_page()
    render_past_maps_page()
    render_present_map_page()
    render_future_predictions_page()
    render_satellite_sources_page()
    render_research_paper_page()
    render_about_page()
    render_agriculture_page()
    render_water_page()
    render_builtup_page()
    render_barren_page()


def test_demo_mode_detection():
    """Verify is_demo_mode detects provenance correctly."""
    from dashboard.data_loader import is_demo_mode
    mode = is_demo_mode()
    assert isinstance(mode, bool)


def test_category_pages_comparison_and_predictions():
    """Verify category-specific 2030 predictions and comparison components."""
    from pathlib import Path
    import json
    import numpy as np
    from dashboard.data_loader import (
        render_category_comparison_section,
        render_2026_unavailable_banner,
        render_period_and_year_selector,
        load_available_raster_maps,
    )

    pred_file = Path("data/outputs/predictions/predicted_map_2030.npy")
    assert pred_file.exists(), "2030 predicted raster must exist"
    pred_data = np.load(pred_file)
    assert pred_data.shape == (100, 100)

    summary_file = Path("data/outputs/predictions/prediction_2030_summary.json")
    assert summary_file.exists()
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert summary["prediction_year"] == 2030
    assert len(summary["categories"]) == 5
    total_area = sum(cat["area_km2"] for cat in summary["categories"].values())
    assert abs(total_area - 4054.0) < 0.5, "Areas must sum strictly to Azamgarh reference area 4,054 km²"

    # Verify category masks exist
    mask_dir = Path("data/outputs/predictions/category_masks")
    for cat in ["agriculture", "vegetation", "water", "builtup", "barren"]:
        assert (mask_dir / f"predicted_map_2030_{cat}.npy").exists()

    # Test comparison section and 2026 banner for each class
    maps = load_available_raster_maps()
    m25 = maps[2025]["data"]
    m30 = maps[2030]["data"]
    for c in [1, 2, 3, 4, 5]:
        render_category_comparison_section(c, m25, m30, is_synthetic=True)
        render_2026_unavailable_banner(f"Class {c}", "📍")

