"""Page: Historical Land-Cover Maps (Past: 2019 & 2022)."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path for direct or multipage execution
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import plotly.express as px
import streamlit as st

from dashboard.data_loader import (
    CLASS_COLORS,
    CLASS_ICONS,
    CLASS_NAMES,
    load_available_raster_maps,
    render_legend_cards,
)
from src.analysis.area_stats import calculate_class_areas


def render_past_maps_page():
    st.markdown('<div class="page-title">🕒 Historical Land-Cover Maps (Past: 2019 & 2022)</div>', unsafe_allow_html=True)
    st.markdown("Explore historical land cover baselines for Azamgarh District prior to recent infrastructure expansion.")

    maps = load_available_raster_maps()
    past_years = [y for y in [2019, 2022] if y in maps]

    if not past_years:
        st.info("Historical map rasters (2019, 2022) not found in `data/outputs/classified/`.")
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
                ticktext=[f"{CLASS_ICONS[c]} {CLASS_NAMES[c]}" for c in [1, 2, 3, 4, 5]],
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Provenance Details Expandable Card
        with st.expander(f"🔍 Provenance Details: {sel_year} Map", expanded=False):
            p1, p2, p3 = st.columns(3)
            with p1:
                st.markdown(f"**Target Year:** `{sel_year}`")
                st.markdown(f"**Period Category:** Historical Past")
                st.markdown(f"**Coverage:** Azamgarh District, UP, India")
            with p2:
                st.markdown(f"**Sensor:** Copernicus Sentinel-2 MSI (Configured)")
                st.markdown(f"**Target Resolution:** 20 m grid")
                st.markdown(f"**Coordinate System:** UTM 44N / WGS84")
            with p3:
                st.markdown(f"**Local Source Path:** `data/outputs/classified/lulc_map_{sel_year}.npy`")
                st.markdown(f"**Total Area:** 4,054.0 km²")

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

        with col_b:
            st.markdown("#### 📅 Intermediate Baseline: 2022")
            fig_b = px.imshow(maps[2022]["data"], color_continuous_scale=color_scale, range_color=[1, 5], aspect="equal")
            fig_b.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=380, coloraxis_showscale=False)
            st.plotly_chart(fig_b, use_container_width=True)

    # Legend
    st.markdown("---")
    render_legend_cards(header="🏷️ Standardized 5-Class Legend")


if __name__ == "__main__":
    render_past_maps_page()
