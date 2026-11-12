"""Page: About & Data Sources - Unified Project Reference, Satellite Sources, and Methodology."""
from __future__ import annotations

import sys
from pathlib import Path

# Reliably ensure repository root and dashboard directory are on sys.path
_current_file = Path(__file__).resolve()
for _cand in [
    _current_file.parent.parent.parent,
    _current_file.parent.parent,
    Path.cwd(),
    Path.cwd().parent,
]:
    if (_cand / "dashboard" / "data_loader.py").is_file():
        if str(_cand) not in sys.path:
            sys.path.insert(0, str(_cand))
        if str(_cand / "dashboard") not in sys.path:
            sys.path.insert(0, str(_cand / "dashboard"))
        break

import pandas as pd
import streamlit as st

try:
    from dashboard.data_loader import (
        CLASS_COLORS,
        CLASS_ICONS,
        CLASS_NAMES,
        is_demo_mode,
        render_legend_cards,
        render_sidebar,
    )
except (ImportError, ModuleNotFoundError):
    from data_loader import (
        CLASS_COLORS,
        CLASS_ICONS,
        CLASS_NAMES,
        is_demo_mode,
        render_legend_cards,
        render_sidebar,
    )


def render_about_page():
    render_sidebar()
    st.markdown('<div class="page-title">ℹ️ About & Data Sources</div>', unsafe_allow_html=True)
    st.markdown("Essential project information, satellite collections, technologies, and methodologies in simple language.")

    # 1. Project Objective and Study Area
    st.markdown("### 📍 1. Project Objective & Study Area")
    st.markdown(
        """
        - **Objective:** Monitor and evaluate land-use and land-cover (LULC) transformations across Azamgarh District over a 16-year timeframe (2019 to 2035).
        - **Core Focus:** Track the preservation of fertile agricultural cropland, identify expanding urban and rural built-up settlements, and project future land scenarios to support sustainable regional planning.
        - **Study Area:** Azamgarh District, located in the eastern Gangetic plains of Uttar Pradesh, India.
          - *Total Area:* **4,054 km²** (Official District Land Records / Census)
          - *Terrain:* Flat alluvial plain bordered to the north by the Ghaghara River and traversed by the meandering Tamsa River.
        """
    )

    st.markdown("---")

    # 2. Data Status: Synthetic vs Real Satellite Data
    st.markdown("### 🔍 2. Current Data Status (Real vs. Synthetic)")
    demo_active = is_demo_mode()
    if demo_active:
        st.markdown(
            """
            <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-left: 5px solid #0284c7; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 18px;">ℹ️</span>
                    <strong style="color: #0369a1; font-size: 15px;">Running in Offline Demonstration Mode</strong>
                </div>
                <div style="font-size: 13.5px; color: #334155; line-height: 1.6;">
                    <p style="margin: 0 0 6px 0;">
                        The dashboard is currently running with <strong>synthetic demonstration rasters</strong> that mimic Azamgarh's land-use patterns.
                        All machine learning pipelines, transition statistics, and projection models are running on this data to showcase full end-to-end functionality without requiring live cloud authentication.
                    </p>
                    <p style="margin: 0 0 6px 0;">
                        <strong>Demonstration vs. Real:</strong> Displayed 2019, 2022, and 2025 maps and 2030/2035 future projections are demonstration outputs.
                    </p>
                    <p style="margin: 0;">
                        <strong>To activate live Google Earth Engine satellite processing:</strong><br>
                        1. Specify your Google Cloud Project ID in <code>.env</code> (e.g., <code>GEE_PROJECT_ID=your-project</code>).<br>
                        2. Run <code>earthengine authenticate</code> in terminal.<br>
                        3. Execute <code>python src/pipeline.py --mode live</code>. The dashboard automatically switches to live satellite mode.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-left: 5px solid #16a34a; padding: 14px; border-radius: 8px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <span style="font-size: 18px;">✅</span>
                    <strong style="color: #166534; font-size: 15px;">Live Satellite Processing Active</strong>
                </div>
                <p style="font-size: 13.5px; color: #15803d; margin: 0; line-height: 1.5;">
                    The system is connected to Google Earth Engine. Displayed classifications and metrics reflect real Copernicus Sentinel-2 observations.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 3. Satellite Data Sources & Official Links
    st.markdown("### 🛰️ 3. Satellite Data Sources & Links")
    st.markdown("The project is built on open-access satellite data from global space agencies:")

    st.markdown(
        """
        | Dataset Name | Sensor / Agency | Purpose in Project | Official Portal |
        | :--- | :--- | :--- | :--- |
        | **Copernicus Sentinel-2 MSI** | Sentinel-2A/B (ESA / EU) | Primary multi-spectral imaging (10–20m resolution) | [Copernicus Data Space](https://browser.dataspace.copernicus.eu/) |
        | **Cloud Score+ V1** | Google Research / Copernicus | Quality masking to remove clouds and cloud shadows | [Cloud Score+ Catalog](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_CLOUD_SCORE_PLUS_V1_S2_HARMONIZED) |
        | **Dynamic World V1** | WRI / Google | Reference benchmark for sample stratification (10m) | [Dynamic World App](https://dynamicworld.app/) |
        | **Landsat 8–9 OLI/TIRS** | USGS / NASA | Historical cross-check sensor (30m resolution) | [USGS EarthExplorer](https://earthexplorer.usgs.gov/) |
        | **FAO GAUL Boundaries** | United Nations FAO | Official district administrative boundary polygon | [FAO GAUL Catalog](https://developers.google.com/earth-engine/datasets/catalog/FAO_GAUL_2015_level2) |
        """
    )

    st.markdown("---")

    # 4. Five Land-Cover Class Definitions
    st.markdown("### 🏷️ 4. Five Land-Cover Class Definitions")
    render_legend_cards(header="")

    st.markdown("---")

    # 5. Tools & Technologies Used
    st.markdown("### 🛠️ 5. Tools & Technologies Used")
    st.markdown(
        """
        | Tool / Library | Role in Project |
        | :--- | :--- |
        | **Python 3.12** | Core programming language for data processing, analysis, and modeling. |
        | **Streamlit** | Powers this clean, interactive web dashboard for user presentations. |
        | **Scikit-Learn (Random Forest)** | Supervised machine learning classifier with 100 decision trees to identify land categories. |
        | **CA-Markov (Cellular Automata)** | Spatial simulation model for projecting future land use in 2030 and 2035. |
        | **Google Earth Engine (GEE)** | Cloud platform for querying, cloud-masking, and compositing satellite images. |
        | **Plotly** | Renders responsive, interactive charts, distribution donuts, and heatmaps. |
        | **Rasterio & NumPy** | Handles numerical array processing and georeferenced GeoTIFF map exports. |
        """
    )

    st.markdown("---")

    # 6. Short Explanation of Random Forest & CA-Markov
    st.markdown("### 🤖 6. How the Machine Learning & Prediction Works")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-top:3px solid #16a34a; border-radius:8px; padding:16px;">
                <h4 style="margin:0 0 8px 0; color:#1b5e20;">🌳 Random Forest Classification</h4>
                <p style="font-size:13.5px; color:#475569; line-height:1.5; margin:0;">
                    1. <strong>Light Reflection:</strong> Different ground covers reflect sunlight differently. For example, green crops reflect near-infrared light, water absorbs it, and concrete reflects shortwave infrared.<br><br>
                    2. <strong>Ensemble of Trees:</strong> The Random Forest model combines 100 independent decision trees. Each tree votes on the class of a pixel, and majority vote decides the final label. This makes the classification stable and accurate.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_m2:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-top:3px solid #7e22ce; border-radius:8px; padding:16px;">
                <h4 style="margin:0 0 8px 0; color:#6b21a8;">🔮 CA-Markov Future Prediction</h4>
                <p style="font-size:13.5px; color:#475569; line-height:1.5; margin:0;">
                    1. <strong>Historical Pace (Markov Chain):</strong> The model measures how quickly land converted between 2019 and 2025 (e.g. rate of farmland becoming built-up).<br><br>
                    2. <strong>Neighborhood Growth (Cellular Automata):</strong> New settlements do not appear randomly; they expand adjacent to existing roads and towns. Combining transition speed with spatial neighborhood contiguity yields realistic future forecasts for 2030 and 2035.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 7. Research References & Limitations
    c_r1, c_r2 = st.columns(2)
    with c_r1:
        st.markdown("### 📚 7. Key Research References")
        st.markdown(
            """
            - **Sentinel-2 Remote Sensing:** Drusch, M., et al. (2012). *Sentinel-2: ESA's optical high-resolution mission for GMES operational services.* Remote Sensing of Environment.
            - **Random Forest Algorithm:** Breiman, L. (2001). *Random Forests.* Machine Learning, 45(1), 5–32.
            - **Model Validation Best Practices:** Olofsson, P., et al. (2014). *Good practices for estimating area and assessing accuracy of land change.* Remote Sensing of Environment.
            - **Land Change Evaluation (Pontius):** Pontius, R. G., et al. (2008). *Comparing the input, output, and validation maps for several models of land change.* The Annals of Regional Science.
            """
        )

    with c_r2:
        st.markdown("### ⚠️ 8. Main Project Limitations")
        st.markdown(
            """
            - **Monsoon Cloud Coverage:** Heavy clouds from July to September limit optical satellite visibility, requiring imagery to be composited during clear Rabi (Feb–Mar) and post-monsoon (Oct–Nov) periods.
            - **Spatial Resolution (20 m):** While suitable for district-level analysis, small features like narrow village alleys or isolated huts can merge with surrounding farmland.
            - **Projection Assumptions:** Future forecasts assume recent historical expansion rates continue at the same pace; major new unexpected infrastructure projects or policy shifts may alter these trajectories.
            """
        )

    # Optional quick-download expander for deliverables
    st.markdown("---")
    with st.expander("💾 Project Deliverables & Research Paper Downloads (Optional)", expanded=False):
        c_dl1, c_dl2 = st.columns(2)
        pdf_path = Path("docs/research_paper/Azamgarh_LULC_Research_Paper.pdf")
        md_path = Path("docs/research_paper/Azamgarh_LULC_Research_Paper.md")

        with c_dl1:
            st.markdown("##### 📄 Research Paper")
            if pdf_path.exists():
                pdf_bytes = pdf_path.read_bytes()
                st.download_button(
                    label=f"📥 Download Paper PDF ({len(pdf_bytes)/(1024*1024):.1f} MB)",
                    data=pdf_bytes,
                    file_name="Azamgarh_LULC_Research_Paper.pdf",
                    mime="application/pdf",
                )
            if md_path.exists():
                st.download_button(
                    label="📝 Download Paper Markdown",
                    data=md_path.read_text(encoding="utf-8"),
                    file_name="Azamgarh_LULC_Research_Paper.md",
                    mime="text/markdown",
                )

        with c_dl2:
            st.markdown("##### 📊 Area Summary Data")
            area_summary_path = Path("data/outputs/change/class_area_summary.csv")
            if area_summary_path.is_file():
                st.download_button(
                    label="📥 Download Class Area Summary (CSV)",
                    data=area_summary_path.read_bytes(),
                    file_name="azamgarh_class_area_summary.csv",
                    mime="text/csv",
                )


if __name__ == "__main__":
    render_about_page()
