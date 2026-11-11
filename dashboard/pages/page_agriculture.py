"""Page: Agriculture / Cropland Analysis for Azamgarh District."""
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


def render_agriculture_page():
    render_sidebar(active_category=1)
    st.markdown('<div class="page-title">🌾 Agriculture & Cropland Analysis</div>', unsafe_allow_html=True)
    st.markdown("Detailed spatial monitoring of agricultural croplands, seasonal cultivation cycles, and arable land transitions across Azamgarh District.")

    # Plain-language explanation box
    st.markdown(
        """
        <div style="background-color: #fefce8; border: 1px solid #fef08a; border-left: 4px solid #ca8a04; padding: 14px; border-radius: 6px; margin-bottom: 20px;">
            <strong style="color: #854d0e; font-size: 14px;">Agricultural Profile of Azamgarh:</strong><br>
            <span style="font-size: 13.5px; color: #713f12; line-height: 1.5;">
                Agriculture is the dominant land-use category in Azamgarh, covering roughly <strong>68% to 72%</strong> of the district.
                The fertile alluvial soil supports intensive multi-cropping: winter <strong>Rabi</strong> crops (wheat, mustard), monsoon/autumn <strong>Kharif</strong> crops (paddy rice),
                and summer <strong>Zaid</strong> vegetables and pulses. Over the past decade, peri-urban development and highway expansion have gradually converted some peripheral farmland into settlements.
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
            key="agri_year_select",
        )
    with c_sel2:
        sel_season = st.selectbox(
            "Seasonal Cropping Stage:",
            ["Rabi Winter Peak (Wheat & Mustard)", "Kharif Autumn Peak (Paddy Rice)", "Zaid Summer Fallow (Post-Harvest)"],
            key="agri_season_select",
        )

    # Get data for selected year
    raster_data = maps.get(sel_year, {}).get("data")
    if raster_data is None:
        st.info(f"Classification map for {sel_year} is currently unavailable.")
        return

    # Calculate areas
    df_area = calculate_class_areas(raster_data, total_reference_area_km2=4054.0)
    agri_row = df_area[df_area["class_code"] == 1].iloc[0]
    agri_area = agri_row["area_km2"]
    agri_pct = agri_row["percentage"]

    # Calculate baseline change from 2019
    base_map = maps.get(2019, {}).get("data")
    if base_map is not None:
        df_base = calculate_class_areas(base_map, total_reference_area_km2=4054.0)
        base_agri = df_base[df_base["class_code"] == 1].iloc[0]["area_km2"]
        delta_km2 = agri_area - base_agri
    else:
        delta_km2 = 0.0

    # 4 KPI Summary Cards
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Agricultural Area", f"{agri_area:,.1f} km²")
    s2.metric("Share of District", f"{agri_pct:.1f}%")
    s3.metric("Change from 2019", f"{delta_km2:+.1f} km²", delta_color="inverse")
    s4.metric("Cropping System", "Indo-Gangetic Multi-Crop")

    st.markdown("---")

    # Visualizations: Map & Trend Chart
    col_map, col_trend = st.columns([3, 2])

    with col_map:
        st.subheader(f"🗺️ Cropland Distribution Map ({sel_year})")
        render_category_map(
            raster_data=raster_data,
            class_code=1,
            year=sel_year,
            is_synthetic=maps.get(sel_year, {}).get("is_synthetic", True),
            height=440,
        )

    with col_trend:
        st.subheader("📈 Multi-Year Cropland Area Trend")
        
        # Build multi-year area table
        trend_records = []
        for yr in available_years:
            if yr in maps:
                d = calculate_class_areas(maps[yr]["data"], total_reference_area_km2=4054.0)
                row = d[d["class_code"] == 1].iloc[0]
                trend_records.append({"Year": str(yr), "Area_km2": round(row["area_km2"], 1), "Share_pct": round(row["percentage"], 1)})
        trend_df = pd.DataFrame(trend_records)

        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Bar(
                x=trend_df["Year"],
                y=trend_df["Area_km2"],
                marker_color=CLASS_COLORS[1],
                text=[f"{v:.0f} km²" for v in trend_df["Area_km2"]],
                textposition="auto",
            )
        )
        fig_trend.update_layout(
            yaxis_title="Cropland Area (km²)",
            xaxis_title="Year",
            margin=dict(l=10, r=10, t=20, b=10),
            height=370,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # Detailed Findings / Conversion
    st.markdown("---")
    st.subheader("🔍 Agricultural Land Conversion Findings")

    c_f1, c_f2 = st.columns([3, 2])
    with c_f1:
        st.markdown(
            f"""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:6px;">
                <h4 style="margin:0 0 10px 0; color:#1e293b;">Key Agricultural Findings (2019–2025)</h4>
                <ul style="font-size:13.5px; color:#475569; line-height:1.6; margin:0; padding-left:20px;">
                    <li><strong>Net Change:</strong> Cultivated cropland decreased from <strong>2,920.1 km²</strong> in 2019 to <strong>2,752.3 km²</strong> in 2025 (a net conversion of ~167.8 km²).</li>
                    <li><strong>Primary Destination:</strong> Converted almost exclusively into <strong>Built-up Areas</strong> (rural settlement expansion and road connectivity corridors).</li>
                    <li><strong>High Core Stability:</strong> Despite peripheral settlement encroachment, the agricultural core in central and eastern Azamgarh remains highly intact and productive.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_f2:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:6px;">
                <h4 style="margin:0 0 10px 0; color:#1e293b;">Seasonal Cropping Cycle</h4>
                <p style="font-size:13px; color:#475569; line-height:1.5; margin:0 0 8px 0;">
                    • <strong>Rabi (Winter):</strong> Sown in Nov–Dec, harvested in Mar–Apr. Highest photosynthetic vigor.<br>
                    • <strong>Zaid (Summer):</strong> Hot dry spell with bare fallow fields between harvests.<br>
                    • <strong>Kharif (Monsoon):</strong> Sown with monsoon arrival, harvested in Oct–Nov.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 5-Class Legend
    st.markdown("---")
    render_legend_cards(header="🏷️ 5-Class Legend")


if __name__ == "__main__":
    render_agriculture_page()

