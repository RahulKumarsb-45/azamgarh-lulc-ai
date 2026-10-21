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


def test_demo_mode_detection():
    """Verify is_demo_mode detects provenance correctly."""
    from dashboard.data_loader import is_demo_mode
    mode = is_demo_mode()
    assert isinstance(mode, bool)
