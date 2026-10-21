"""Page 7: Dataset Catalogue, Audit Summary, and Data Downloads."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path for direct or multipage execution
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import io
import pandas as pd
import streamlit as st

from dashboard.data_loader import load_audit_data


DATASET_CATALOGUE = [
    {
        "Dataset Name": "Sentinel-2 Surface Reflectance (Harmonized)",
        "Earth Engine ID": "COPERNICUS/S2_SR_HARMONIZED",
        "Spatial Resolution": "10 m – 20 m",
        "Temporal Range": "2017-03-28 to Present",
        "Bands Utilized": "B2, B3, B4, B8, B11, B12",
        "Licensing / Access": "Open Access (Copernicus Free & Open)",
        "Role in Project": "Core historical mapping sensor",
    },
    {
        "Dataset Name": "Cloud Score+ for Sentinel-2",
        "Earth Engine ID": "GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED",
        "Spatial Resolution": "10 m – 20 m",
        "Temporal Range": "2017 to Present",
        "Bands Utilized": "cs_cdf",
        "Licensing / Access": "Open / Google Research",
        "Role in Project": "Cloud and cloud-shadow masking (threshold 0.6)",
    },
    {
        "Dataset Name": "Dynamic World V1",
        "Earth Engine ID": "GOOGLE/DYNAMICWORLD/V1",
        "Spatial Resolution": "10 m",
        "Temporal Range": "2015 to Present",
        "Bands Utilized": "label, water, crops, trees, built",
        "Licensing / Access": "Open Access (CC-BY 4.0)",
        "Role in Project": "Reference guide & sampling stratification only",
    },
    {
        "Dataset Name": "Landsat 8-9 Collection 2 Level-2",
        "Earth Engine ID": "LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2",
        "Spatial Resolution": "30 m",
        "Temporal Range": "2013 to Present",
        "Bands Utilized": "SR_B2..SR_B7",
        "Licensing / Access": "USGS / NASA Open Data",
        "Role in Project": "Cross-sensor audit & historical fallback",
    },
    {
        "Dataset Name": "FAO GAUL Administrative Boundaries",
        "Earth Engine ID": "FAO/GAUL/2015/level2",
        "Spatial Resolution": "Vector polygons",
        "Temporal Range": "2015",
        "Bands Utilized": "ADM2_NAME (Azamgarh)",
        "Licensing / Access": "FAO Non-Commercial License",
        "Role in Project": "Official district boundary spatial clipping",
    },
]


def render_downloads_page():
    st.markdown('<div class="page-title">📦 Dataset Catalogue & Export Downloads</div>', unsafe_allow_html=True)
    st.markdown("Access comprehensive metadata catalogues, scientific citations, satellite data audit reports, and downloadable artifacts.")

    tab_cat, tab_audit, tab_dl = st.tabs(["📚 Earth Engine Dataset Catalogue", "🔍 Satellite Audit Summary", "💾 Download Artifacts"])

    with tab_cat:
        st.subheader("🛰️ Remote Sensing Dataset Catalogue")
        cat_df = pd.DataFrame(DATASET_CATALOGUE)
        st.dataframe(cat_df, use_container_width=True)

        st.markdown("""
        **Academic Citations & Documented Standards:**
        - **Sentinel-2 L2A:** Drusch, M., et al. (2012). *Sentinel-2: ESA's optical high-resolution mission for GMES operational services.* Remote Sensing of Environment, 120, 25-36.
        - **Cloud Score+:** Pasquarella, V. J., et al. (2023). *Cloud Score+: Global cloud and cloud-shadow masking for Sentinel-2.* Earth Engine Data Catalog.
        - **Dynamic World:** Brown, C. F., et al. (2022). *Dynamic World, Near real-time global 10m land use land cover mapping.* Scientific Data, 9(1), 251.
        - **Validation Good Practices:** Olofsson, P., et al. (2014). *Good practices for estimating area and assessing accuracy of land change.* Remote Sensing of Environment, 148, 42-57.
        """)

    with tab_audit:
        st.subheader("📋 Phase 0 Data-Availability Audit Results")
        audit_data = load_audit_data()

        if audit_data["is_available"] and audit_data["boundary"] is not None:
            st.markdown("**1. District Boundary Verification:**")
            st.dataframe(audit_data["boundary"], use_container_width=True)

            if audit_data["s2_audit"] is not None:
                st.markdown("**2. Sentinel-2 Seasonal Observation Flags:**")
                st.dataframe(audit_data["s2_audit"], use_container_width=True)

            if audit_data["summary_md"]:
                st.markdown("**3. Summary Report:**")
                st.markdown(audit_data["summary_md"])
        else:
            st.info("""
            **Audit Status:** Live Earth Engine audit outputs have not yet been generated in `data/outputs/audit/`.
            
            To execute the live audit on your authenticated account:
            ```powershell
            python -m src.data.data_audit
            ```
            This queries the live Earth Engine catalog across 40 seasonal windows (2016–2025) and generates `boundary_report.csv`, `s2_year_season_audit.csv`, and `audit_summary.md`.
            """)

    with tab_dl:
        st.subheader("💾 Exportable Data Tables & Products")
        st.markdown("Download generated tabular datasets, georeferenced rasters, and reports:")

        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            st.markdown("##### 📊 Tabular Metrics & Schemas")
            # 1. Class Schema
            schema_path = Path("config/class_schema.yaml")
            if schema_path.is_file():
                st.download_button(
                    label="📥 Download Class Schema (YAML)",
                    data=schema_path.read_bytes(),
                    file_name="azamgarh_class_schema.yaml",
                    mime="text/yaml",
                )

            # 2. Area Summary CSV
            area_summary_path = Path("data/outputs/change/class_area_summary.csv")
            if area_summary_path.is_file():
                st.download_button(
                    label="📥 Download Historical Area Statistics (CSV)",
                    data=area_summary_path.read_bytes(),
                    file_name="azamgarh_class_area_summary.csv",
                    mime="text/csv",
                )

            # 3. Critical Transitions CSV
            crit_path = Path("data/outputs/change/critical_transitions_2019_2025.csv")
            if crit_path.is_file():
                st.download_button(
                    label="📥 Download Critical Transitions (CSV)",
                    data=crit_path.read_bytes(),
                    file_name="azamgarh_critical_transitions_2019_2025.csv",
                    mime="text/csv",
                )

            # 4. Olofsson Adjusted Areas CSV
            olofsson_path = Path("data/outputs/metrics/olofsson_adjusted_areas.csv")
            if olofsson_path.is_file():
                st.download_button(
                    label="📥 Download Olofsson Area-Adjusted Accuracy (CSV)",
                    data=olofsson_path.read_bytes(),
                    file_name="azamgarh_olofsson_adjusted_areas.csv",
                    mime="text/csv",
                )

            # 5. Provenance Manifest JSON
            prov_path = Path("data/outputs/provenance.json")
            if prov_path.is_file():
                st.download_button(
                    label="📥 Download Provenance Manifest (JSON)",
                    data=prov_path.read_bytes(),
                    file_name="azamgarh_provenance_manifest.json",
                    mime="application/json",
                )

        with col_dl2:
            st.markdown("##### 🗺️ Georeferenced GeoTIFF Rasters & Reports")
            # 6. Classified 2025 GeoTIFF
            tif_2025 = Path("data/outputs/classified/lulc_map_2025.tif")
            if tif_2025.is_file():
                st.download_button(
                    label="📥 Download 2025 Classified Map (GeoTIFF)",
                    data=tif_2025.read_bytes(),
                    file_name="azamgarh_lulc_2025.tif",
                    mime="image/tiff",
                )

            # 7. Projected 2035 GeoTIFF
            tif_2035 = Path("data/outputs/predictions/predicted_map_2035.tif")
            if tif_2035.is_file():
                st.download_button(
                    label="📥 Download 2035 Projected Map (GeoTIFF)",
                    data=tif_2035.read_bytes(),
                    file_name="azamgarh_predicted_2035.tif",
                    mime="image/tiff",
                )

            # 8. Synthetic Reference Samples
            syn_samples = Path("data/synthetic_fixture/synthetic_reference_samples.csv")
            if syn_samples.is_file():
                st.download_button(
                    label="📥 Download Synthetic Reference Samples (CSV)",
                    data=syn_samples.read_bytes(),
                    file_name="azamgarh_synthetic_reference_samples.csv",
                    mime="text/csv",
                )

            # 9. Project Report
            report_path = Path("docs/project_report.md")
            if report_path.is_file():
                st.download_button(
                    label="📥 Download B.Tech Academic Project Report (Markdown)",
                    data=report_path.read_bytes(),
                    file_name="azamgarh_lulc_project_report.md",
                    mime="text/markdown",
                )


if __name__ == "__main__":
    render_downloads_page()
