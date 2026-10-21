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

from dashboard.data_loader import is_demo_mode


def render_satellite_sources_page():
    st.markdown('<div class="page-title">🛰️ Satellite Image Dates, Sensors & Data Provenance</div>', unsafe_allow_html=True)
    st.markdown(
        "Complete provenance audit separating raw Earth Observation imagery from derived LULC classifications and simulated projections."
    )

    if is_demo_mode():
        st.warning(
            "⚠️ **OFFLINE PROVENANCE STATUS:** The current workspace is operating in **Demonstration Mode** using verified synthetic fixtures. "
            "No active Earth Engine tokens were detected in `~/.config/earthengine/credentials`. "
            "Live scene acquisition dates are verified via the configured Phase 0 audit schema below."
        )

    st.markdown("""
    ### 📌 Image Provenance & Processing Lineage
    In remote sensing research, data integrity requires a strict trace:
    ```
    Raw Spacecraft Granule → Surface Reflectance (L2A) → Cloud Score+ Masking → Seasonal Medoid Composite → Random Forest → Classified LULC
    ```
    """)

    # Tabbed views
    tab_sensors, tab_windows, tab_granules, tab_audit = st.tabs([
        "🛰️ Configured Satellite Sensors & Datasets",
        "📅 Observation Windows & Compositing Dates",
        "🏷️ Raw Imagery vs Classified Maps Lineage",
        "🔍 Data Verification & Audit Protocol",
    ])

    with tab_sensors:
        st.markdown("#### Configured Earth Observation Collections")
        datasets = [
            {
                "Role": "Primary LULC Classification",
                "Sensor / Platform": "Copernicus Sentinel-2A/B MSI",
                "Dataset Collection ID": "COPERNICUS/S2_SR_HARMONIZED",
                "Provider": "ESA / European Union / Copernicus",
                "Spatial Res": "10 m / 20 m",
                "Spectral Bands Used": "B2 (Blue), B3 (Green), B4 (Red), B8 (NIR), B11 (SWIR1), B12 (SWIR2)",
                "Official URL": "https://browser.dataspace.copernicus.eu/",
                "Verification": "Configured in settings.yaml",
            },
            {
                "Role": "Atmospheric & Cloud Masking",
                "Sensor / Platform": "Sentinel-2 Cloud Score+ V1",
                "Dataset Collection ID": "GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED",
                "Provider": "Google / Copernicus",
                "Spatial Res": "10 m / 20 m",
                "Spectral Bands Used": "cs_cdf (Usability threshold > 0.60)",
                "Official URL": "https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_CLOUD_SCORE_PLUS_V1_S2_HARMONIZED",
                "Verification": "Configured in settings.yaml",
            },
            {
                "Role": "Independent Reference / Benchmark",
                "Sensor / Platform": "Dynamic World V1",
                "Dataset Collection ID": "GOOGLE/DYNAMICWORLD/V1",
                "Provider": "World Resources Institute / Google",
                "Spatial Res": "10 m",
                "Spectral Bands Used": "9 Near-real-time land cover probability bands",
                "Official URL": "https://dynamicworld.app/",
                "Verification": "Configured in settings.yaml",
            },
            {
                "Role": "Long-Term Historical Fallback",
                "Sensor / Platform": "Landsat 8/9 OLI/TIRS Tier 1 L2",
                "Dataset Collection ID": "LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2",
                "Provider": "USGS / NASA",
                "Spatial Res": "30 m",
                "Spectral Bands Used": "SR_B2, SR_B3, SR_B4, SR_B5, SR_B6, SR_B7",
                "Official URL": "https://earthexplorer.usgs.gov/",
                "Verification": "Configured in settings.yaml",
            },
            {
                "Role": "District Administrative Boundary",
                "Sensor / Platform": "FAO GAUL 2015 (Level 2)",
                "Dataset Collection ID": "FAO/GAUL/2015/level2",
                "Provider": "UN Food and Agriculture Organization",
                "Spatial Res": "Vector Polygons",
                "Spectral Bands Used": "ADM2_NAME == 'Azamgarh', ADM1_NAME == 'Uttar Pradesh'",
                "Official URL": "https://developers.google.com/earth-engine/datasets/catalog/FAO_GAUL_2015_level2",
                "Verification": "Configured in settings.yaml",
            },
        ]
        st.dataframe(pd.DataFrame(datasets), use_container_width=True)

    with tab_windows:
        st.markdown("#### Seasonal Observation Windows for Azamgarh District")
        st.markdown(
            "Due to intense tropical cloud cover during the Indian Summer Monsoon, single-date satellite images often "
            "suffer from cloud contamination. The pipeline implements a **multi-temporal seasonal medoid composite** strategy:"
        )

        windows = [
            {
                "Target Year": 2019,
                "Season": "Rabi (Winter/Spring Peak Crops)",
                "Configured Date Range": "2019-02-01 to 2019-03-31",
                "Compositing Method": "Cloud Score+ Filtered Medoid (B2, B3, B4, B8, B11, B12)",
                "MGRS Footprint Tiles": "44RPQ, 44RPP, 44RQQ, 44RQP",
                "Active Status in Workspace": "⚠️ Synthetic demonstration raster on disk",
            },
            {
                "Target Year": 2019,
                "Season": "Post-Monsoon (Autumn Baseline)",
                "Configured Date Range": "2019-10-01 to 2019-11-30",
                "Compositing Method": "Cloud Score+ Filtered Medoid",
                "MGRS Footprint Tiles": "44RPQ, 44RPP, 44RQQ, 44RQP",
                "Active Status in Workspace": "⚠️ Synthetic demonstration raster on disk",
            },
            {
                "Target Year": 2022,
                "Season": "Rabi (Winter/Spring Peak Crops)",
                "Configured Date Range": "2022-02-01 to 2022-03-31",
                "Compositing Method": "Cloud Score+ Filtered Medoid",
                "MGRS Footprint Tiles": "44RPQ, 44RPP, 44RQQ, 44RQP",
                "Active Status in Workspace": "⚠️ Synthetic demonstration raster on disk",
            },
            {
                "Target Year": 2022,
                "Season": "Post-Monsoon (Autumn Baseline)",
                "Configured Date Range": "2022-10-01 to 2022-11-30",
                "Compositing Method": "Cloud Score+ Filtered Medoid",
                "MGRS Footprint Tiles": "44RPQ, 44RPP, 44RQQ, 44RQP",
                "Active Status in Workspace": "⚠️ Synthetic demonstration raster on disk",
            },
            {
                "Target Year": 2025,
                "Season": "Rabi (Contemporary Baseline)",
                "Configured Date Range": "2025-02-01 to 2025-03-31",
                "Compositing Method": "Cloud Score+ Filtered Medoid",
                "MGRS Footprint Tiles": "44RPQ, 44RPP, 44RQQ, 44RQP",
                "Active Status in Workspace": "⚠️ Synthetic demonstration raster on disk",
            },
        ]
        st.dataframe(pd.DataFrame(windows), use_container_width=True)

        st.info(
            "📌 **Reporting Rule:** Rather than fabricating a single artificial acquisition date (e.g. 'March 15, 2019') for "
            "a multi-scene composite, the project reports the exact **observation date window** over which surface reflectance "
            "medoids were computed."
        )

    with tab_granules:
        st.markdown("#### Raw Satellite Imagery vs Derived Classified Rasters")
        st.markdown(
            "To prevent scientific ambiguity, the table below documents every input and output file currently tracked in the repository:"
        )

        traceability = [
            {
                "Item Type": "Classified LULC Map",
                "Target Year": 2019,
                "File Path": "data/outputs/classified/lulc_map_2019.npy",
                "GeoTIFF Path": "data/outputs/classified/lulc_map_2019.tif",
                "Data Nature": "Categorical Raster (Values 1-5)",
                "Current Origin": "Synthetic fixture matching Azamgarh agricultural spatial structure",
                "Exact Scene Date": "DATE NOT VERIFIED (Simulated offline baseline)",
            },
            {
                "Item Type": "Classified LULC Map",
                "Target Year": 2022,
                "File Path": "data/outputs/classified/lulc_map_2022.npy",
                "GeoTIFF Path": "data/outputs/classified/lulc_map_2022.tif",
                "Data Nature": "Categorical Raster (Values 1-5)",
                "Current Origin": "Synthetic fixture matching Azamgarh agricultural spatial structure",
                "Exact Scene Date": "DATE NOT VERIFIED (Simulated offline baseline)",
            },
            {
                "Item Type": "Classified LULC Map",
                "Target Year": 2025,
                "File Path": "data/outputs/classified/lulc_map_2025.npy",
                "GeoTIFF Path": "data/outputs/classified/lulc_map_2025.tif",
                "Data Nature": "Categorical Raster (Values 1-5)",
                "Current Origin": "Synthetic fixture matching Azamgarh agricultural spatial structure",
                "Exact Scene Date": "DATE NOT VERIFIED (Simulated offline baseline)",
            },
            {
                "Item Type": "Forecast Simulation",
                "Target Year": 2030,
                "File Path": "data/outputs/predictions/predicted_map_2030.npy",
                "GeoTIFF Path": "data/outputs/predictions/predicted_map_2030.tif",
                "Data Nature": "Projected Raster (Values 1-5)",
                "Current Origin": "CA-Markov mathematical projection (Seed: 2030, Iterations: 5)",
                "Exact Scene Date": "N/A — MODEL PREDICTION (NOT A SATELLITE OBSERVATION)",
            },
            {
                "Item Type": "Forecast Simulation",
                "Target Year": 2035,
                "File Path": "data/outputs/predictions/predicted_map_2035.npy",
                "GeoTIFF Path": "data/outputs/predictions/predicted_map_2035.tif",
                "Data Nature": "Projected Raster (Values 1-5)",
                "Current Origin": "CA-Markov mathematical projection (Seed: 2035, Iterations: 5)",
                "Exact Scene Date": "N/A — MODEL PREDICTION (NOT A SATELLITE OBSERVATION)",
            },
        ]
        st.dataframe(pd.DataFrame(traceability), use_container_width=True)

    with tab_audit:
        st.markdown("#### 🔬 Running the Live Data Audit (`src/data/data_audit.py`)")
        st.markdown("""
        The repository includes a dedicated zero-cache provenance auditor script:
        ```bash
        python src/data/data_audit.py
        ```
        **Audit Capabilities:**
        - Authenticates directly against Google Earth Engine using official Google Cloud project credentials.
        - Verifies exact Sentinel-2 granule IDs across MGRS tiles `44RPQ`, `44RPP`, `44RQQ`, and `44RQP`.
        - Calculates live cloud-free scene availability before and after applying Cloud Score+ thresholds.
        - Generates timestamped audit outputs in `data/outputs/audit/` with live API response times.
        """)


if __name__ == "__main__":
    render_satellite_sources_page()
