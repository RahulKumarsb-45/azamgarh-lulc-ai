"""Main Streamlit Application Controller for Azamgarh LULC Monitoring & Research System.

Integrated Sections:
1. Past LULC Maps (Historical: 2019, 2022)
2. Present/Recent LULC Map (Contemporary: 2025)
3. Future Prediction Maps (CA-Markov: 2030, 2035)
4. Change Detection (Past vs Present Transitions)
5. Satellite Image Dates & Sources (Data Provenance)
6. Research Paper PDF & Publication Figures (PDF Viewer & Download)
7. System Overview & Executive Summary
8. Vegetation Dynamics (NDVI Phenology)
9. Model Accuracy & Validation Metrics
10. Raw Data, Rasters & GeoTIFF Downloads
11. Complete Project Data & Tools Documentation
"""
from __future__ import annotations

import streamlit as st

from dashboard.data_loader import is_demo_mode
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

# Configure Page
st.set_page_config(
    page_title="Azamgarh LULC Monitoring & Prediction System",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional CSS Styling
CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 10px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .main-header h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
    }
    .main-header p {
        margin: 6px 0 0 0;
        font-size: 14.5px;
        opacity: 0.92;
        color: #e8f5e9;
    }

    .page-title {
        font-size: 22px;
        font-weight: 700;
        color: #1b5e20;
        margin-bottom: 14px;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 8px;
    }

    .kpi-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        text-align: center;
        border-top: 4px solid #2e7d32;
    }
    .kpi-title {
        font-size: 13px;
        color: #616161;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-val {
        font-size: 24px;
        font-weight: 700;
        color: #212121;
        margin: 6px 0 2px 0;
    }
    .kpi-sub {
        font-size: 12px;
        color: #757575;
    }

    /* Sidebar adjustments */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    .sidebar-badge {
        background-color: #e8f5e9;
        color: #1b5e20;
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


def main():
    # Sidebar Navigation
    with st.sidebar:
        st.markdown('<span class="sidebar-badge">B.Tech Minor Project</span>', unsafe_allow_html=True)
        st.markdown("### 🛰️ Research Navigation")

        pages = {
            # Core Research Deliverables Requested by User
            "🕒 Past LULC Maps": render_past_maps_page,
            "📍 Present/Recent LULC Map": render_present_map_page,
            "🔮 Future Prediction Maps": render_future_predictions_page,
            "📈 Change Detection": render_change_page,
            "🛰️ Satellite Image Dates & Sources": render_satellite_sources_page,
            "📄 Research Paper PDF": render_research_paper_page,
            # Supporting Analytics & Diagnostics
            "🌿 System Overview": render_overview_page,
            "🌱 Vegetation (NDVI)": render_vegetation_page,
            "🎯 Model Accuracy": render_accuracy_page,
            "📦 Data & Downloads": render_downloads_page,
            "📖 Master Project Documentation": render_documentation_page,
        }

        selected_page = st.radio(
            "Select Section:",
            list(pages.keys()),
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("**Study Area:** Azamgarh, UP, India")
        if is_demo_mode():
            st.markdown("**Data Mode:** ⚠️ Synthetic / Demo Fixture")
            st.caption("Live Sentinel-2 pending Earth Engine auth")
        else:
            st.markdown("**Sensor:** Sentinel-2 SR (10–20 m)")
        st.markdown("**ML Model:** Random Forest + CA-Markov")

        st.markdown("---")
        st.caption("Azamgarh LULC Research | Final Year CSE")

    # Render Selected Page
    render_func = pages[selected_page]
    render_func()


if __name__ == "__main__":
    main()
