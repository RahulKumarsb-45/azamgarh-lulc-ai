"""Page 2: Interactive Land-Cover Maps (Past, Present & Future)."""
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
    render_sidebar,
)
from src.analysis.area_stats import calculate_class_areas


def _format_year_label(year: int | str) -> str:
    y = int(year) if str(year).isdigit() else year
    if y in (2019, 2022):
        return f"{y} (Historical Past)"
    elif y == 2025:
        return f"{y} (Present Baseline)"
    elif y in (2030, 2035):
        return f"{y} (Future Simulation)"
    return str(y)


def render_maps_page():
    render_sidebar()
    st.markdown('<div class="page-title">🗺️ LULC Classification</div>', unsafe_allow_html=True)
    st.markdown("Explore past and present land-use and land-cover classification maps for Azamgarh District.")

    maps = load_available_raster_maps()
    if not maps:
        st.info("No classification raster maps currently detected in `data/outputs/classified/`.")
        return

    available_years = sorted(maps.keys())

    # Mode Selector
    c_ctrl1, c_ctrl2 = st.columns([2, 3])
    with c_ctrl1:
        view_mode = st.radio("Display Mode:", ["Single Year Map", "Compare Two Years Side-by-Side"], horizontal=True)

    color_scale = [
        [0.0, CLASS_COLORS[1]], [0.2, CLASS_COLORS[1]],
        [0.2, CLASS_COLORS[2]], [0.4, CLASS_COLORS[2]],
        [0.4, CLASS_COLORS[3]], [0.6, CLASS_COLORS[3]],
        [0.6, CLASS_COLORS[4]], [0.8, CLASS_COLORS[4]],
        [0.8, CLASS_COLORS[5]], [1.0, CLASS_COLORS[5]],
    ]

    if view_mode == "Single Year Map":
        with c_ctrl2:
            selected_year = st.selectbox(
                "Select Year:",
                available_years,
                index=available_years.index(2025) if 2025 in available_years else len(available_years) - 1,
                format_func=_format_year_label,
            )

        raster_data = maps[selected_year]["data"]
        year_label = _format_year_label(selected_year)

        st.markdown(f"#### 📍 Azamgarh LULC Map — **{year_label}**")

        # Large, clear interactive map
        fig = px.imshow(
            raster_data,
            color_continuous_scale=color_scale,
            range_color=[1, 5],
            labels=dict(color="Class"),
            aspect="equal",
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=580,
            coloraxis_colorbar=dict(
                title="LULC Category",
                tickvals=[1, 2, 3, 4, 5],
                ticktext=[f"{CLASS_ICONS[c]} {CLASS_NAMES[c]}" for c in [1, 2, 3, 4, 5]],
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Area Statistics Summary for the Selected Year
        st.markdown(f"#### 📊 Area Summary for {selected_year}")
        df_area = calculate_class_areas(raster_data, total_reference_area_km2=4054.0)
        
        # Summary metrics
        m_cols = st.columns(5)
        for idx, c in enumerate([1, 2, 3, 4, 5]):
            row = df_area[df_area["class_code"] == c].iloc[0]
            with m_cols[idx]:
                st.metric(
                    label=f"{CLASS_ICONS[c]} {CLASS_NAMES[c]}",
                    value=f"{row['area_km2']:.1f} km²",
                    delta=f"{row['percentage']:.1f}% share",
                    delta_color="off",
                )

    else:
        # Side-by-side comparison mode
        col_y1, col_y2 = st.columns(2)
        with col_y1:
            y1 = st.selectbox(
                "First Year:",
                available_years,
                index=0,
                format_func=_format_year_label,
                key="maps_comp_y1",
            )
        with col_y2:
            y2 = st.selectbox(
                "Second Year:",
                available_years,
                index=available_years.index(2025) if 2025 in available_years else len(available_years) - 1,
                format_func=_format_year_label,
                key="maps_comp_y2",
            )

        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown(f"#### 📅 {_format_year_label(y1)}")
            fig_a = px.imshow(
                maps[y1]["data"],
                color_continuous_scale=color_scale,
                range_color=[1, 5],
                aspect="equal",
            )
            fig_a.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=440, coloraxis_showscale=False)
            st.plotly_chart(fig_a, use_container_width=True)

        with c_b:
            st.markdown(f"#### 📅 {_format_year_label(y2)}")
            fig_b = px.imshow(
                maps[y2]["data"],
                color_continuous_scale=color_scale,
                range_color=[1, 5],
                aspect="equal",
            )
            fig_b.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=440, coloraxis_showscale=False)
            st.plotly_chart(fig_b, use_container_width=True)

    # 5-Class Legend Cards
    st.markdown("---")
    render_legend_cards(header="🏷️ 5-Class Legend & Definitions")


if __name__ == "__main__":
    render_maps_page()
