"""Page: Historical Land-Cover Maps (Past: 2019 & 2022)."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import plotly.express as px
import streamlit as st

from dashboard.data_loader import (
    CLASS_COLORS,
    CLASS_NAMES,
    is_demo_mode,
    load_available_raster_maps,
)
from src.analysis.area_stats import calculate_class_areas


def render_past_maps_page():
    st.markdown('<div class="page-title">🕒 Historical Land-Cover Maps (Past: 2019 & 2022)</div>', unsafe_allow_html=True)
    st.markdown("Explore verified historical land cover baselines for Azamgarh District prior to recent infrastructure expansion.")

    if is_demo_mode():
        st.warning(
            "⚠️ **DEMO / SYNTHETIC DATA — NOT VALIDATED SATELLITE RESULTS**\n\n"
            "The historical maps below are loaded from demonstration verification rasters (`data/outputs/classified/`). "
            "To generate genuine Copernicus Sentinel-2 L2A classifications for 2019 and 2022, configure your Google Cloud project in `.env` and execute `python src/pipeline.py --mode live`."
        )

    maps = load_available_raster_maps()
    past_years = [y for y in [2019, 2022] if y in maps]

    if not past_years:
        st.error("Historical map rasters (2019, 2022) not found in `data/outputs/classified/`.")
        return

    c_ctrl1, c_ctrl2 = st.columns([2, 3])
    with c_ctrl1:
        view_mode = st.radio("Display Mode:", ["Single Year View", "Side-by-Side Comparison (2019 vs 2022)"], horizontal=True)

    color_scale = [
        [0.0, CLASS_COLORS[1]], [0.2, CLASS_COLORS[1]],
        [0.2, CLASS_COLORS[2]], [0.4, CLASS_COLORS[2]],
        [0.4, CLASS_COLORS[3]], [0.6, CLASS_COLORS[3]],
        [0.6, CLASS_COLORS[4]], [0.8, CLASS_COLORS[4]],
        [0.8, CLASS_COLORS[5]], [1.0, CLASS_COLORS[5]],
    ]

    if view_mode == "Single Year View":
        with c_ctrl2:
            sel_year = st.selectbox("Select Historical Year:", past_years, index=0)

        map_info = maps[sel_year]
        raster_data = map_info["data"]

        # Plotly categorical heatmap
        fig = px.imshow(
            raster_data,
            color_continuous_scale=color_scale,
            range_color=[1, 5],
            labels=dict(color="Class"),
            aspect="equal",
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=500,
            coloraxis_colorbar=dict(
                title="LULC Class",
                tickvals=[1, 2, 3, 4, 5],
                ticktext=[CLASS_NAMES[c] for c in [1, 2, 3, 4, 5]],
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Provenance Details Expandable Card
        with st.expander(f"🔍 Source, Acquisition & Provenance Details: {sel_year} Map", expanded=True):
            p1, p2, p3 = st.columns(3)
            with p1:
                st.markdown(f"**Target Year:** `{sel_year}`")
                st.markdown(f"**Period Category:** Historical Past")
                st.markdown(f"**Observation Window:** Rabi (Feb 1 – Mar 31) & Post-Monsoon (Oct 1 – Nov 30)")
                st.markdown(f"**Coverage:** Azamgarh District, UP, India")
            with p2:
                st.markdown(f"**Sensor:** Copernicus Sentinel-2 MSI (Configured)")
                st.markdown(f"**Collection ID:** `COPERNICUS/S2_SR_HARMONIZED`")
                st.markdown(f"**Target Resolution:** 20 m (100×100 grid)")
                st.markdown(f"**Coordinate System:** UTM 44N / WGS84")
            with p3:
                st.markdown(f"**Current Data Status:** ⚠️ `SYNTHETIC FIXTURE`")
                st.markdown(f"**Local Source Path:** `data/outputs/classified/lulc_map_{sel_year}.npy`")
                st.markdown(f"**Processing Engine:** 100-Tree Random Forest + Cloud Score+")
                st.markdown(f"**Total Area:** 4,054.0 km² (Conserved)")

            # Area statistics
            df_area = calculate_class_areas(raster_data, total_reference_area_km2=4054.0)
            st.markdown(f"**Estimated Class Area Breakdown ({sel_year}):**")
            st.dataframe(df_area[["class_name", "area_km2", "area_ha", "percentage"]].rename(columns={
                "class_name": "Class Name",
                "area_km2": "Area (km²)",
                "area_ha": "Area (Hectares)",
                "percentage": "Share (%)",
            }), use_container_width=True)

    else:
        # Comparison mode
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### 📅 Historical Baseline: 2019")
            fig_a = px.imshow(maps[2019]["data"], color_continuous_scale=color_scale, range_color=[1, 5], aspect="equal")
            fig_a.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=380, coloraxis_showscale=False)
            st.plotly_chart(fig_a, use_container_width=True)
            st.caption("Source: `data/outputs/classified/lulc_map_2019.npy` (Synthetic Fixture)")

        with col_b:
            st.markdown("#### 📅 Intermediate Baseline: 2022")
            fig_b = px.imshow(maps[2022]["data"], color_continuous_scale=color_scale, range_color=[1, 5], aspect="equal")
            fig_b.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=380, coloraxis_showscale=False)
            st.plotly_chart(fig_b, use_container_width=True)
            st.caption("Source: `data/outputs/classified/lulc_map_2022.npy` (Synthetic Fixture)")

    # Legend
    st.markdown("---")
    st.markdown("### 🏷️ Standardized 5-Class Legend")
    l_cols = st.columns(5)
    for idx, c in enumerate([1, 2, 3, 4, 5]):
        with l_cols[idx]:
            st.markdown(
                f'<div style="background-color: {CLASS_COLORS[c]}; color: {"#000" if c in [1,5] else "#fff"}; '
                f'padding: 8px; border-radius: 6px; font-weight: bold; text-align: center; margin-bottom: 6px;">'
                f'Class {c}: {CLASS_NAMES[c]}</div>',
                unsafe_allow_html=True,
            )
