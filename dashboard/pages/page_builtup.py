"""Page: Built-up Area & Urban Settlement Analysis for Azamgarh District."""
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


def render_builtup_page():
    render_sidebar(active_category=4)
    st.markdown('<div class="page-title">🏙️ Built-up Area & Settlement Analysis</div>', unsafe_allow_html=True)
    st.markdown("Detailed spatial monitoring of urban sprawl, rural settlement densification, and infrastructure expansion across Azamgarh District.")

    # Plain-language explanation box
    st.markdown(
        """
        <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-left: 4px solid #ef4444; padding: 14px; border-radius: 6px; margin-bottom: 20px;">
            <strong style="color: #991b1b; font-size: 14px;">Urbanization Profile of Azamgarh:</strong><br>
            <span style="font-size: 13.5px; color: #7f1d1d; line-height: 1.5;">
                Built-up and settlement surfaces have experienced the most rapid expansion in Azamgarh District.
                Covering approximately <strong>510.8 km² (12.6%)</strong> in 2019, settlements expanded to <strong>678.6 km² (16.7%)</strong> by 2025.
                This growth reflects both concentric outward expansion around Azamgarh City and linear corridor ribbon development along highways such as the Purvanchal Expressway.
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
            key="builtup_year_select",
        )
    with c_sel2:
        sel_filter = st.selectbox(
            "Settlement Zone Focus:",
            ["District-wide Settlements", "Azamgarh Urban Agglomeration & Tehsil Towns", "Radial Highway & Expressway Corridors"],
            key="builtup_filter_select",
        )

    # Get data for selected year
    raster_data = maps.get(sel_year, {}).get("data")
    if raster_data is None:
        st.info(f"Classification map for {sel_year} is currently unavailable.")
        return

    # Calculate areas
    df_area = calculate_class_areas(raster_data, total_reference_area_km2=4054.0)
    built_row = df_area[df_area["class_code"] == 4].iloc[0]
    built_area = built_row["area_km2"]
    built_pct = built_row["percentage"]

    # Calculate baseline change from 2019
    base_map = maps.get(2019, {}).get("data")
    if base_map is not None:
        df_base = calculate_class_areas(base_map, total_reference_area_km2=4054.0)
        base_built = df_base[df_base["class_code"] == 4].iloc[0]["area_km2"]
        delta_km2 = built_area - base_built
    else:
        delta_km2 = 0.0

    # 4 KPI Summary Cards
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Built-up Area", f"{built_area:,.1f} km²")
    s2.metric("Share of District", f"{built_pct:.1f}%")
    s3.metric("Change from 2019", f"{delta_km2:+.1f} km²", delta_color="normal")
    s4.metric("Growth Driver", "Transit Corridors & Sprawl")

    st.markdown("---")

    # Visualizations: Map & Trend Chart
    col_map, col_trend = st.columns([3, 2])

    with col_map:
        st.subheader(f"🗺️ Built-up Distribution Map ({sel_year})")
        render_category_map(
            raster_data=raster_data,
            class_code=4,
            year=sel_year,
            is_synthetic=maps.get(sel_year, {}).get("is_synthetic", True),
            height=440,
        )

    with col_trend:
        st.subheader("📈 Multi-Year Built-up Expansion Trend")
        trend_records = []
        for yr in available_years:
            if yr in maps:
                d = calculate_class_areas(maps[yr]["data"], total_reference_area_km2=4054.0)
                row = d[d["class_code"] == 4].iloc[0]
                trend_records.append({"Year": str(yr), "Area_km2": round(row["area_km2"], 1), "Share_pct": round(row["percentage"], 1)})
        trend_df = pd.DataFrame(trend_records)

        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Bar(
                x=trend_df["Year"],
                y=trend_df["Area_km2"],
                marker_color=CLASS_COLORS[4],
                text=[f"{v:.0f} km²" for v in trend_df["Area_km2"]],
                textposition="auto",
            )
        )
        fig_trend.update_layout(
            yaxis_title="Built-up Area (km²)",
            xaxis_title="Year",
            margin=dict(l=10, r=10, t=20, b=10),
            height=370,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # Detailed Findings / Expansion Hotspots
    st.markdown("---")
    st.subheader("🔍 Urban Encroachment & Infrastructure Expansion")

    c_f1, c_f2 = st.columns([3, 2])
    with c_f1:
        st.markdown(
            f"""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:6px;">
                <h4 style="margin:0 0 10px 0; color:#1e293b;">Key Built-up Findings (2019–2025)</h4>
                <ul style="font-size:13.5px; color:#475569; line-height:1.6; margin:0; padding-left:20px;">
                    <li><strong>Rapid Growth:</strong> Total settlement and built-up land grew by <strong>+167.8 km² (+32.9%)</strong> between 2019 and 2025.</li>
                    <li><strong>Origin of Growth:</strong> Expansion occurred almost entirely through conversion of fertile agricultural cropland.</li>
                    <li><strong>Spatial Clustering:</strong> Concentrated along the Purvanchal Expressway interchanges and radial state highways connecting Azamgarh to Varanasi, Mau, and Gorakhpur.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_f2:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:6px;">
                <h4 style="margin:0 0 10px 0; color:#1e293b;">Urban Growth Characteristics</h4>
                <p style="font-size:13px; color:#475569; line-height:1.5; margin:0;">
                    • <strong>Irreversible Conversion:</strong> Once agricultural land is paved and converted into masonry structures, it rarely reverts to farmland.<br>
                    • <strong>Village Infill:</strong> Rural homesteads (abadi lands) are progressively densifying.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 5-Class Legend
    st.markdown("---")
    render_legend_cards(header="🏷️ 5-Class Legend")


if __name__ == "__main__":
    render_builtup_page()

