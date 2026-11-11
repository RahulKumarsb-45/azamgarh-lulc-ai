"""Page: Satellite Image Dates, Collections & Complete Data Provenance."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path for direct or multipage execution
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import streamlit as st

from dashboard.data_loader import is_demo_mode, render_legend_cards


def render_satellite_sources_page():
    st.markdown('<div class="page-title">🛰️ Satellite Data Sources & Collections</div>', unsafe_allow_html=True)
    st.markdown(
        "Complete catalog of Earth Observation imagery collections, spectral bands, and spatial resolutions configured for Azamgarh District."
    )

    st.markdown("""
    ### 📌 Image Provenance & Processing Lineage
    In remote sensing research, data integrity requires a strict trace:
    ```
    Raw Spacecraft Granule → Surface Reflectance (L2A) → Cloud Score+ Masking → Seasonal Medoid Composite → Random Forest → Classified LULC
    ```
    """)

    datasets = [
        {
            "Role": "Primary LULC Classification",
            "Sensor / Platform": "Copernicus Sentinel-2A/B MSI",
            "Dataset Collection ID": "COPERNICUS/S2_SR_HARMONIZED",
            "Provider": "ESA / European Union / Copernicus",
            "Spatial Res": "10 m / 20 m",
            "Spectral Bands Used": "B2 (Blue), B3 (Green), B4 (Red), B8 (NIR), B11 (SWIR1), B12 (SWIR2)",
            "Official URL": "https://browser.dataspace.copernicus.eu/",
        },
        {
            "Role": "Atmospheric & Cloud Masking",
            "Sensor / Platform": "Sentinel-2 Cloud Score+ V1",
            "Dataset Collection ID": "GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED",
            "Provider": "Google / Copernicus",
            "Spatial Res": "10 m / 20 m",
            "Spectral Bands Used": "cs_cdf (Usability threshold > 0.60)",
            "Official URL": "https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_CLOUD_SCORE_PLUS_V1_S2_HARMONIZED",
        },
        {
            "Role": "Independent Reference / Benchmark",
            "Sensor / Platform": "Dynamic World V1",
            "Dataset Collection ID": "GOOGLE/DYNAMICWORLD/V1",
            "Provider": "World Resources Institute / Google",
            "Spatial Res": "10 m",
            "Spectral Bands Used": "9 Near-real-time land cover probability bands",
            "Official URL": "https://dynamicworld.app/",
        },
        {
            "Role": "Long-Term Historical Fallback",
            "Sensor / Platform": "Landsat 8/9 OLI/TIRS Tier 1 L2",
            "Dataset Collection ID": "LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2",
            "Provider": "USGS / NASA",
            "Spatial Res": "30 m",
            "Spectral Bands Used": "SR_B2, SR_B3, SR_B4, SR_B5, SR_B6, SR_B7",
            "Official URL": "https://earthexplorer.usgs.gov/",
        },
        {
            "Role": "District Administrative Boundary",
            "Sensor / Platform": "FAO GAUL 2015 (Level 2)",
            "Dataset Collection ID": "FAO/GAUL/2015/level2",
            "Provider": "UN Food and Agriculture Organization",
            "Spatial Res": "Vector Polygons",
            "Spectral Bands Used": "ADM2_NAME == 'Azamgarh', ADM1_NAME == 'Uttar Pradesh'",
            "Official URL": "https://developers.google.com/earth-engine/datasets/catalog/FAO_GAUL_2015_level2",
        },
    ]

    st.subheader("🛰️ Configured Earth Observation Collections")
    st.dataframe(pd.DataFrame(datasets), use_container_width=True)

    st.markdown("---")
    render_legend_cards(header="🏷️ 5-Class Legend")


if __name__ == "__main__":
    render_satellite_sources_page()
