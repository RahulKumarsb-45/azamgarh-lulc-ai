"""Page 2: Interactive Land-Cover Maps and Multi-Year Spatial Viewer."""
from __future__ import annotations

import folium
import numpy as np
import plotly.express as px
import streamlit as st
from streamlit_folium import folium_static

from dashboard.data_loader import (
    CLASS_COLORS,
    CLASS_NAMES,
    is_demo_mode,
    load_available_raster_maps,
)


def render_maps_page():
    st.markdown('<div class="page-title">🗺️ Interactive Land-Cover Maps</div>', unsafe_allow_html=True)
    st.markdown("Explore classified Sentinel-2 land cover maps with class toggles, side-by-side temporal comparison, and interactive spatial inspection.")

    if is_demo_mode():
        st.warning(
            "⚠️ **DEMO / SYNTHETIC DATA — NOT VALIDATED SATELLITE RESULTS**\n\n"
            "The maps displayed below are synthetic demonstration rasters. "
            "To generate authentic Copernicus Sentinel-2 L2A classified GeoTIFFs, run `python src/pipeline.py --mode live` with authenticated GEE credentials."
        )

    maps = load_available_raster_maps()
    available_years = sorted(maps.keys())

    if not available_years:
        st.warning("No classification raster maps currently detected in `data/outputs/classified/`. Please run the classification pipeline.")
        return

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])
    with col_ctrl1:
        view_mode = st.radio("Display Mode:", ["Single Year", "Side-by-Side Comparison"], horizontal=True)

    if view_mode == "Single Year":
        with col_ctrl2:
            selected_year = st.selectbox("Select Year:", available_years, index=len(available_years) - 1)
        
        map_info = maps[selected_year]
        raster_data = map_info["data"]

        # Color mapping preview
        st.markdown(f"**Viewing:** Land Cover Map for **{selected_year}** {'(Synthetic Test Fixture)' if map_info.get('is_synthetic') else '(Sentinel-2 L2A Classified)'}")

        # Interactive Plotly Heatmap with exact categorical colors
        color_scale = [
            [0.0, CLASS_COLORS[1]], [0.2, CLASS_COLORS[1]],
            [0.2, CLASS_COLORS[2]], [0.4, CLASS_COLORS[2]],
            [0.4, CLASS_COLORS[3]], [0.6, CLASS_COLORS[3]],
            [0.6, CLASS_COLORS[4]], [0.8, CLASS_COLORS[4]],
            [0.8, CLASS_COLORS[5]], [1.0, CLASS_COLORS[5]],
        ]

        fig = px.imshow(
            raster_data,
            color_continuous_scale=color_scale,
            range_color=[1, 5],
            labels=dict(color="Class"),
            aspect="equal",
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=550,
            coloraxis_colorbar=dict(
                title="LULC Class",
                tickvals=[1, 2, 3, 4, 5],
                ticktext=[CLASS_NAMES[c] for c in [1, 2, 3, 4, 5]],
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        # Comparison mode
        with col_ctrl2:
            year_a = st.selectbox("Base Year (T1):", available_years, index=0)
        with col_ctrl3:
            year_b = st.selectbox("Comparison Year (T2):", available_years, index=len(available_years) - 1)

        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown(f"#### 📅 Year: {year_a}")
            fig_a = px.imshow(
                maps[year_a]["data"],
                color_continuous_scale=[
                    [0.0, CLASS_COLORS[1]], [0.2, CLASS_COLORS[1]],
                    [0.2, CLASS_COLORS[2]], [0.4, CLASS_COLORS[2]],
                    [0.4, CLASS_COLORS[3]], [0.6, CLASS_COLORS[3]],
                    [0.6, CLASS_COLORS[4]], [0.8, CLASS_COLORS[4]],
                    [0.8, CLASS_COLORS[5]], [1.0, CLASS_COLORS[5]],
                ],
                range_color=[1, 5],
                aspect="equal",
            )
            fig_a.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=420, coloraxis_showscale=False)
            st.plotly_chart(fig_a, use_container_width=True)

        with c_b:
            st.markdown(f"#### 📅 Year: {year_b}")
            fig_b = px.imshow(
                maps[year_b]["data"],
                color_continuous_scale=[
                    [0.0, CLASS_COLORS[1]], [0.2, CLASS_COLORS[1]],
                    [0.2, CLASS_COLORS[2]], [0.4, CLASS_COLORS[2]],
                    [0.4, CLASS_COLORS[3]], [0.6, CLASS_COLORS[3]],
                    [0.6, CLASS_COLORS[4]], [0.8, CLASS_COLORS[4]],
                    [0.8, CLASS_COLORS[5]], [1.0, CLASS_COLORS[5]],
                ],
                range_color=[1, 5],
                aspect="equal",
            )
            fig_b.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=420, coloraxis_showscale=False)
            st.plotly_chart(fig_b, use_container_width=True)

    # Class Legend Card
    st.markdown("---")
    st.markdown("### 🏷️ 5-Class Legend & Definitions")
    l_cols = st.columns(5)
    for idx, c in enumerate([1, 2, 3, 4, 5]):
        with l_cols[idx]:
            st.markdown(
                f'<div style="background-color: {CLASS_COLORS[c]}; color: {"#000" if c in [1,5] else "#fff"}; '
                f'padding: 8px; border-radius: 6px; font-weight: bold; text-align: center; margin-bottom: 6px;">'
                f'Class {c}: {CLASS_NAMES[c]}</div>',
                unsafe_allow_html=True,
            )
            if c == 1:
                st.caption("Seasonal crops (wheat, paddy, mustard) with high rabi/zaid NDVI swing.")
            elif c == 2:
                st.caption("Perennial orchards, groves, dense tree canopies with sustained greenness.")
            elif c == 3:
                st.caption("Tamsa river, oxbow lakes, ponds, and open irrigation channels.")
            elif c == 4:
                st.caption("Azamgarh urban agglomeration, rural settlements, roads, impervious surface.")
            elif c == 5:
                st.caption("Perennially bare soil, open fallow, sandbanks along floodplains.")
