"""Spatial analysis, area statistics, change detection, and NDVI trends."""
from src.analysis.area_stats import (
    calculate_class_areas,
    calculate_gain_loss,
    summarize_multi_year_areas,
)
from src.analysis.change_detection import (
    detect_land_cover_changes,
    extract_critical_transitions,
    identify_change_hotspots,
)
from src.analysis.vegetation import (
    analyze_ndvi_trend,
    detect_vegetation_decline_hotspots,
    calculate_ndvi_summary_statistics,
)

__all__ = [
    "calculate_class_areas",
    "calculate_gain_loss",
    "summarize_multi_year_areas",
    "detect_land_cover_changes",
    "extract_critical_transitions",
    "identify_change_hotspots",
    "analyze_ndvi_trend",
    "detect_vegetation_decline_hotspots",
    "calculate_ndvi_summary_statistics",
]
