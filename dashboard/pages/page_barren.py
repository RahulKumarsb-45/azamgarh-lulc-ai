"""Page: Barren & Open Land Analysis for Azamgarh District."""
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


def render_barren_page():
    render_sidebar(active_category=5)
    st.markdown('<div class="page-title">🏜️ Barren & Open Land Analysis</div>', unsafe_allow_html=True)
    st.markdown("Detailed spatial monitoring of uncultivated open land, sandy riverbeds, exposed soils, and vacant plots across Azamgarh District.")

    # Plain-language explanation box
    st.markdown(
        """
        <div style="background-color: #efebe9; border: 1px solid #d7ccc8; border-left: 4px solid #8d6e63; padding: 14px; border-radius: 6px; margin-bottom: 20px;">
            <strong style="color: #4e342e; font-size: 14px;">Barren & Open Land Profile of Azamgarh:</strong><br>
            <span style="font-size: 13.5px; color: #3e2723; line-height: 1.5;">
                In the fertile Gangetic alluvium of Azamgarh, perennially barren land represents a modest <strong>2.0% to 2.5%</strong> (around 90 to 100 km²) of total land area.
                This category comprises exposed sandy deposits along the floodplains of the Ghaghara and Tamsa rivers, fallow uncultivated plots,
                brick-kiln excavations, and vacant cleared land awaiting construction.
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
            key="barren_year_select",
        )
    with c_sel2:
        sel_type = st.selectbox(
            "Open Land Characterization:",
            ["All Barren & Open Surfaces", "Riparian Riverbed Sands (Ghaghara/Tamsa)", "Vacant / Cleared Construction Soil"],
            key="barren_type_select",
        )

    # Get data for selected year
    raster_data = maps.get(sel_year, {}).get("data")
    if raster_data is None:
        st.info(f"Classification map for {sel_year} is currently unavailable.")
        return

    # Calculate areas
    df_area = calculate_class_areas(raster_data, total_reference_area_km2=4054.0)
    barren_row = df_area[df_area["class_code"] == 5].iloc[0]
    barren_area = barren_row["area_km2"]
    barren_pct = barren_row["percentage"]

    # Calculate baseline change from 2019
    base_map = maps.get(2019, {}).get("data")
    if base_map is not None:
        df_base = calculate_class_areas(base_map, total_reference_area_km2=4054.0)
        base_barren = df_base[df_base["class_code"] == 5].iloc[0]["area_km2"]
        delta_km2 = barren_area - base_barren
    else:
        delta_km2 = 0.0

    # 4 KPI Summary Cards
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Barren / Open Area", f"{barren_area:,.1f} km²")
    s2.metric("Share of District", f"{barren_pct:.1f}%")
    s3.metric("Change from 2019", f"{delta_km2:+.1f} km²")
    s4.metric("Primary Features", "Floodplain Sand & Bare Soil")

    st.markdown("---")

    # Visualizations: Map & Trend Chart
    col_map, col_trend = st.columns([3, 2])

    with col_map:
        st.subheader(f"🗺️ Barren Land Distribution Map ({sel_year})")
        render_category_map(
            raster_data=raster_data,
            class_code=5,
            year=sel_year,
            is_synthetic=maps.get(sel_year, {}).get("is_synthetic", True),
            height=440,
        )

    with col_trend:
        st.subheader("📈 Multi-Year Barren Land Area Trend")
        trend_records = []
        for yr in available_years:
            if yr in maps:
                d = calculate_class_areas(maps[yr]["data"], total_reference_area_km2=4054.0)
                row = d[d["class_code"] == 5].iloc[0]
                trend_records.append({"Year": str(yr), "Area_km2": round(row["area_km2"], 1), "Share_pct": round(row["percentage"], 1)})
        trend_df = pd.DataFrame(trend_records)

        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Bar(
                x=trend_df["Year"],
                y=trend_df["Area_km2"],
                marker_color=CLASS_COLORS[5],
                text=[f"{v:.0f} km²" for v in trend_df["Area_km2"]],
                textposition="auto",
            )
        )
        fig_trend.update_layout(
            yaxis_title="Barren Area (km²)",
            xaxis_title="Year",
            margin=dict(l=10, r=10, t=20, b=10),
            height=370,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # Detailed Findings / Conversions
    st.markdown("---")
    st.subheader("🔍 Land Dynamics & Conversion Patterns")

    c_f1, c_f2 = st.columns([3, 2])
    with c_f1:
        st.markdown(
            f"""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:6px;">
                <h4 style="margin:0 0 10px 0; color:#1e293b;">Key Barren Land Findings (2019–2025)</h4>
                <ul style="font-size:13.5px; color:#475569; line-height:1.6; margin:0; padding-left:20px;">
                    <li><strong>Overall Extent:</strong> Barren and open land covers approximately <strong>91.2 km² (~2.25%)</strong> of Azamgarh District.</li>
                    <li><strong>Riverbed Fluvial Shifts:</strong> Sand deposits along the Ghaghara and Tamsa riverbeds shift boundaries after seasonal monsoon floods.</li>
                    <li><strong>Intermediate Land Stage:</strong> Pockets of bare land often act as a temporary intermediate stage during construction—fields are cleared of crops before foundations and roads are laid.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_f2:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:6px;">
                <h4 style="margin:0 0 10px 0; color:#1e293b;">Bare Soil vs. Seasonal Fallow</h4>
                <p style="font-size:13px; color:#475569; line-height:1.5; margin:0;">
                    • <strong>Distinction:</strong> Temporary post-harvest crop fallow (in May) is classified as agricultural land because of seasonal NDVI swings.<br>
                    • <strong>Perennially Barren:</strong> Only permanently un-vegetated soil and sandbanks are designated in this class.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 5-Class Legend
    st.markdown("---")
    render_legend_cards(header="🏷️ 5-Class Legend")


if __name__ == "__main__":
    render_barren_page()

