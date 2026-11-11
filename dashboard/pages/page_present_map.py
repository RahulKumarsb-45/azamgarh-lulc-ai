"""Page: Present / Recent Land-Cover Map (2025)."""
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


def render_present_map_page():
    st.markdown('<div class="page-title">📍 Contemporary Land-Cover Map (Present / Recent: 2025)</div>', unsafe_allow_html=True)
    st.markdown(
        "Observation and classification of Azamgarh District's contemporary landscape, reflecting recent "
        "infrastructure corridors and rural settlements."
    )

    maps = load_available_raster_maps()
    if 2025 not in maps:
        st.info("2025 classified raster map not found in `data/outputs/classified/`.")
        return

    raster_data = maps[2025]["data"]
    df_area = calculate_class_areas(raster_data, total_reference_area_km2=4054.0)

    # Key Metrics Bar
    m1, m2, m3, m4, m5 = st.columns(5)
    for idx, c in enumerate([1, 2, 3, 4, 5]):
        col = [m1, m2, m3, m4, m5][idx]
        row = df_area[df_area["class_code"] == c].iloc[0]
        col.metric(
            label=f"{CLASS_ICONS[c]} {CLASS_NAMES[c]}",
            value=f"{row['area_km2']:.1f} km²",
            delta=f"{row['percentage']:.1f}% share",
            delta_color="off",
        )

    st.markdown("---")

    # Map Visual
    c_map, c_info = st.columns([3, 2])

    color_scale = [
        [0.0, CLASS_COLORS[1]], [0.2, CLASS_COLORS[1]],
        [0.2, CLASS_COLORS[2]], [0.4, CLASS_COLORS[2]],
        [0.4, CLASS_COLORS[3]], [0.6, CLASS_COLORS[3]],
        [0.6, CLASS_COLORS[4]], [0.8, CLASS_COLORS[4]],
        [0.8, CLASS_COLORS[5]], [1.0, CLASS_COLORS[5]],
    ]

    with c_map:
        st.markdown("#### 🗺️ 2025 Classified LULC Raster (Azamgarh District)")
        fig = px.imshow(
            raster_data,
            color_continuous_scale=color_scale,
            range_color=[1, 5],
            labels=dict(color="Class"),
            aspect="equal",
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=460,
            coloraxis_colorbar=dict(
                title="LULC Class",
                tickvals=[1, 2, 3, 4, 5],
                ticktext=[f"{CLASS_ICONS[c]} {CLASS_NAMES[c]}" for c in [1, 2, 3, 4, 5]],
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c_info:
        st.markdown("#### 📊 Land Allocation Summary")
        fig_donut = px.pie(
            df_area,
            names="class_name",
            values="area_km2",
            color="class_name",
            color_discrete_map={row["class_name"]: CLASS_COLORS[row["class_code"]] for _, row in df_area.iterrows()},
            hole=0.45,
        )
        fig_donut.update_layout(margin=dict(l=0, r=0, t=20, b=10), height=300, showlegend=True)
        st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown(
            """
            **Landscape Breakdown:**
            - **Cropland** dominates **~70.1%** of district territory, sustaining multi-crop farming.
            - **Built-up lands** cover **~14.6%**, showing concentrated growth around Azamgarh city and transport spines.
            """
        )

    # Full Area Table
    st.markdown("#### 📋 2025 Class Area Distribution Table")
    st.dataframe(
        df_area[["class_code", "class_name", "area_km2", "area_ha", "percentage", "pixel_count"]].rename(columns={
            "class_code": "Code",
            "class_name": "Class Name",
            "area_km2": "Area (km²)",
            "area_ha": "Area (ha)",
            "percentage": "Share (%)",
            "pixel_count": "Grid Pixels",
        }),
        use_container_width=True,
    )

    # Legend
    st.markdown("---")
    render_legend_cards(header="🏷️ Standardized 5-Class Legend")


if __name__ == "__main__":
    render_present_map_page()
