"""Main Streamlit Application Controller for Azamgarh LULC Monitoring & Prediction System.

Navigation Structure:
- Main Navigation:
  1. Home
  2. LULC Classification
  3. Change Detection
  4. Future Prediction
  5. About & Data Sources

- Land Cover Analysis (Five Dedicated Class Pages):
  1. 🌾 Agriculture Analysis
  2. 🌳 Vegetation Analysis
  3. 💧 Water Bodies Analysis
  4. 🏙️ Built-up Area Analysis
  5. 🏜️ Barren / Open Land Analysis
"""
from __future__ import annotations

import sys
from pathlib import Path

# 1. Reliably add repository root to sys.path before any project imports
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# 2. Verify dashboard package directory
_dashboard_pkg = REPO_ROOT / "dashboard"
_data_loader_mod = _dashboard_pkg / "data_loader.py"
if not (_dashboard_pkg.is_dir() and _data_loader_mod.is_file()):
    for _candidate in [Path(__file__).parent.parent.absolute(), Path.cwd(), Path.cwd().parent]:
        if (_candidate / "dashboard" / "data_loader.py").is_file():
            REPO_ROOT = _candidate
            if str(REPO_ROOT) not in sys.path:
                sys.path.insert(0, str(REPO_ROOT))
            break

assert (REPO_ROOT / "dashboard").is_dir(), f"dashboard package directory not found at {REPO_ROOT}"
assert (REPO_ROOT / "dashboard" / "data_loader.py").is_file(), f"data_loader.py not found at {REPO_ROOT}/dashboard"

import streamlit as st

from dashboard.pages.page1_overview import render_overview_page
from dashboard.pages.page2_maps import render_maps_page
from dashboard.pages.page3_change import render_change_page
from dashboard.pages.page4_vegetation import render_vegetation_page
from dashboard.pages.page_about_data_sources import render_about_page
from dashboard.pages.page_agriculture import render_agriculture_page
from dashboard.pages.page_barren import render_barren_page
from dashboard.pages.page_builtup import render_builtup_page
from dashboard.pages.page_future_predictions import render_future_predictions_page
from dashboard.pages.page_water import render_water_page

# Configure Page
st.set_page_config(
    page_title="Azamgarh LULC Monitoring & Prediction Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean, Modern Professional CSS Styling
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #1e293b;
    }

    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #1e3a1e 0%, #2e7d32 100%);
        color: #ffffff;
        padding: 24px 28px;
        border-radius: 10px;
        margin-bottom: 22px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    }
    .main-header h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.3px;
    }
    .main-header p {
        margin: 6px 0 0 0;
        font-size: 14.5px;
        opacity: 0.92;
        color: #e8f5e9;
        line-height: 1.4;
    }

    /* Page Section Title */
    .page-title {
        font-size: 22px;
        font-weight: 700;
        color: #1e3a1e;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }

    /* KPI Summary Cards */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px 14px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        text-align: center;
        border-top: 4px solid #2e7d32;
    }
    .kpi-title {
        font-size: 12.5px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-val {
        font-size: 23px;
        font-weight: 700;
        color: #0f172a;
        margin: 6px 0 2px 0;
    }
    .kpi-sub {
        font-size: 12px;
        color: #64748b;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    .sidebar-badge {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 12px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


MAIN_PAGES = {
    "🏠 Home": render_overview_page,
    "🗺️ LULC Classification": render_maps_page,
    "📈 Change Detection": render_change_page,
    "🔮 Future Prediction": render_future_predictions_page,
    "ℹ️ About & Data Sources": render_about_page,
}

ANALYSIS_PAGES = {
    "🌾 Agriculture Analysis": render_agriculture_page,
    "🌳 Vegetation Analysis": render_vegetation_page,
    "💧 Water Bodies Analysis": render_water_page,
    "🏙️ Built-up Area Analysis": render_builtup_page,
    "🏜️ Barren / Open Land Analysis": render_barren_page,
}


from dashboard.data_loader import render_sidebar


def main():
    render_sidebar()
    render_overview_page()


if __name__ == "__main__":
    main()
