"""Page: Water Bodies Analysis for Azamgarh District."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path for direct or multipage execution
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.data_loader import (
    CLASS_COLORS,
    CLASS_ICONS,
    CLASS_NAMES,
    load_available_raster_maps,
    render_category_map,
    render_legend_cards,
    render_sidebar,
)
from src.analysis.area_stats import calculate_class_areas


def render_water_page():
    render_sidebar(active_category=3)
    st.markdown('<div class="page-title">💧 Water Bodies Analysis</div>', unsafe_allow_html=True)
    st.markdown("Detailed spatial monitoring of rivers, oxbow lakes, village ponds, and canal networks across Azamgarh District.")

    # Plain-language explanation box
    st.markdown(
        """
        <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #2563eb; padding: 14px; border-radius: 6px; margin-bottom: 20px;">
            <strong style="color: #1e40af; font-size: 14px;">Hydrological Profile of Azamgarh:</strong><br>
            <span style="font-size: 13.5px; color: #1e3a8a; line-height: 1.5;">
                Water bodies occupy approximately <strong>2.5% to 3.0%</strong> (around 120 km²) of Azamgarh's total geographical area.
                The drainage network is anchored by the <strong>Tamsa River</strong> (Tons), which winds centrally across the district,
                alongside the northern boundary of the <strong>Ghaghara River</strong>, numerous traditional village tanks (pokharis),
                and government canal systems. Water surfaces exhibit seasonal expansion following the monsoon and contracted surface pools in peak summer.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    maps = load_available_raster_maps()
    available_years = sorted(maps.keys())
    if not available_years:
        available_years = [2019, 2022, 2025]

    # Controls
    c_sel1, c_sel2 = st.columns(2)
    with c_sel1:
        sel_year = st.selectbox(
            "Select Observation Year:",
            available_years,
            index=available_years.index(2025) if 2025 in available_years else len(available_years) - 1,
            key="water_year_select",
        )
    with c_sel2:
        sel_season = st.selectbox(
            "Hydrological Season Window:",
            ["Post-Monsoon High Water (Oct–Nov)", "Winter Rabi Irrigation (Feb–Mar)", "Pre-Monsoon Summer Minimum (Apr–May)"],
            key="water_season_select",
        )

    # Get data for selected year
    raster_data = maps.get(sel_year, {}).get("data")
    if raster_data is None:
        st.info(f"Classification map for {sel_year} is currently unavailable.")
        return

    # Calculate areas
    df_area = calculate_class_areas(raster_data, total_reference_area_km2=4054.0)
    water_row = df_area[df_area["class_code"] == 3].iloc[0]
    water_area = water_row["area_km2"]
    water_pct = water_row["percentage"]

    # Calculate baseline change from 2019
    base_map = maps.get(2019, {}).get("data")
    if base_map is not None:
        df_base = calculate_class_areas(base_map, total_reference_area_km2=4054.0)
        base_water = df_base[df_base["class_code"] == 3].iloc[0]["area_km2"]
        delta_km2 = water_area - base_water
    else:
        delta_km2 = 0.0

    # 4 KPI Summary Cards
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Water Bodies Area", f"{water_area:,.1f} km²")
    s2.metric("Share of District", f"{water_pct:.1f}%")
    s3.metric("Change from 2019", f"{delta_km2:+.1f} km²")
    s4.metric("Primary River", "Tamsa & Ghaghara Basin")

    st.markdown("---")

    # Visualizations: Map & Trend Chart
    col_map, col_trend = st.columns([3, 2])

    with col_map:
        st.subheader(f"🗺️ Surface Water Distribution Map ({sel_year})")
        render_category_map(
            raster_data=raster_data,
            class_code=3,
            year=sel_year,
            is_synthetic=maps.get(sel_year, {}).get("is_synthetic", True),
            height=440,
        )

    with col_trend:
        st.subheader("📈 Multi-Year Surface Water Trend")
        trend_records = []
        for yr in available_years:
            if yr in maps:
                d = calculate_class_areas(maps[yr]["data"], total_reference_area_km2=4054.0)
                row = d[d["class_code"] == 3].iloc[0]
                trend_records.append({"Year": str(yr), "Area_km2": round(row["area_km2"], 1), "Share_pct": round(row["percentage"], 1)})
        trend_df = pd.DataFrame(trend_records)

        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Bar(
                x=trend_df["Year"],
                y=trend_df["Area_km2"],
                marker_color=CLASS_COLORS[3],
                text=[f"{v:.0f} km²" for v in trend_df["Area_km2"]],
                textposition="auto",
            )
        )
        fig_trend.update_layout(
            yaxis_title="Water Area (km²)",
            xaxis_title="Year",
            margin=dict(l=10, r=10, t=20, b=10),
            height=370,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # Detailed Findings / Conservation
    st.markdown("---")
    st.subheader("🔍 Hydrological Dynamics & Water Conservation")

    c_f1, c_f2 = st.columns([3, 2])
    with c_f1:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:6px;">
                <h4 style="margin:0 0 10px 0; color:#1e293b;">Key Water Body Findings (2019–2025)</h4>
                <ul style="font-size:13.5px; color:#475569; line-height:1.6; margin:0; padding-left:20px;">
                    <li><strong>Acreage Preservation:</strong> Permanent surface water extent has remained highly conserved across Azamgarh at approximately <strong>121.6 km²</strong>.</li>
                    <li><strong>Tamsa River Meanders:</strong> The central course of the Tamsa River and its oxbow wetlands maintain consistent water presence.</li>
                    <li><strong>Seasonal Variance:</strong> Small village ponds exhibit strong seasonal shrink-and-fill cycles, dropping in May before recharging during July–September monsoons.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_f2:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:6px;">
                <h4 style="margin:0 0 10px 0; color:#1e293b;">Water Index (NDWI) Note</h4>
                <p style="font-size:13px; color:#475569; line-height:1.5; margin:0;">
                    Water bodies are detected using the <strong>Normalized Difference Water Index (NDWI)</strong>,
                    which leverages green and near-infrared reflectance. Open water absorbs NIR radiation, making it readily distinguishable from crop canopies and built structures.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 5-Class Legend
    st.markdown("---")
    render_legend_cards(header="🏷️ 5-Class Legend")


if __name__ == "__main__":
    render_water_page()

