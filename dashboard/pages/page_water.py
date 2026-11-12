"""Page: Water Bodies Analysis for Azamgarh District."""
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

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    from dashboard.data_loader import (
        CLASS_COLORS,
        CLASS_ICONS,
        CLASS_NAMES,
        load_available_raster_maps,
        render_2026_unavailable_banner,
        render_category_comparison_section,
        render_category_map,
        render_legend_cards,
        render_period_and_year_selector,
        render_sidebar,
    )
except (ImportError, ModuleNotFoundError):
    from data_loader import (
        CLASS_COLORS,
        CLASS_ICONS,
        CLASS_NAMES,
        load_available_raster_maps,
        render_2026_unavailable_banner,
        render_category_comparison_section,
        render_category_map,
        render_legend_cards,
        render_period_and_year_selector,
        render_sidebar,
    )

try:
    from src.analysis.area_stats import calculate_class_areas
except (ImportError, ModuleNotFoundError):
    _cand = Path(__file__).resolve().parent.parent.parent
    if str(_cand) not in sys.path:
        sys.path.insert(0, str(_cand))
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
        available_years = [2019, 2022, 2025, 2030]

    # Period and Year Selector (Past, Present 2026, Future 2030)
    period_type, sel_year = render_period_and_year_selector("water", available_years)

    if period_type == "present":
        # 2026 is not available offline; display clear, honest notice
        render_2026_unavailable_banner("Water Bodies", "💧")
    else:
        # Get data for selected year
        raster_data = maps.get(sel_year, {}).get("data")
        is_synthetic = maps.get(sel_year, {}).get("is_synthetic", True)

        if raster_data is None:
            st.info(f"Classification map for {sel_year} is currently unavailable.")
        else:
            # Calculate dynamic areas
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
            delta_label = "Change from 2019" if sel_year != 2019 else "Baseline Year"
            s3.metric(delta_label, f"{delta_km2:+.1f} km²")
            s4.metric("Primary River", "Tamsa & Ghaghara Basin")

            st.markdown("---")

            # Visualizations: Map & Trend Chart
            col_map, col_trend = st.columns([3, 2])

            with col_map:
                year_label = f"{sel_year} (Predicted)" if period_type == "future" else str(sel_year)
                st.subheader(f"🗺️ Surface Water Distribution Map ({year_label})")
                render_category_map(
                    raster_data=raster_data,
                    class_code=3,
                    year=year_label,
                    is_synthetic=is_synthetic,
                    height=440,
                )

            with col_trend:
                st.subheader("📈 Multi-Year Surface Water Trend")
                trend_years = [y for y in [2019, 2022, 2025, 2030] if y in maps]
                trend_records = []
                for yr in trend_years:
                    d = calculate_class_areas(maps[yr]["data"], total_reference_area_km2=4054.0)
                    row = d[d["class_code"] == 3].iloc[0]
                    tag = f"{yr}*" if yr == 2030 else str(yr)
                    trend_records.append({
                        "Year": tag,
                        "Area_km2": round(row["area_km2"], 1),
                        "Share_pct": round(row["percentage"], 1),
                    })
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
                    xaxis_title="Observation Year (* = Projected)",
                    margin=dict(l=10, r=10, t=20, b=10),
                    height=370,
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#f8fafc",
                )
                st.plotly_chart(fig_trend, use_container_width=True)

            # Detailed Findings / Conservation
            st.markdown("---")
            st.subheader("🔍 Hydrological Dynamics & Water Conservation")

            c_f1, c_f2 = st.columns([3, 2])
            with c_f1:
                # Dynamic historical figures
                m19 = maps.get(2019, {}).get("data")
                m25 = maps.get(2025, {}).get("data")
                w19 = calculate_class_areas(m19, total_reference_area_km2=4054.0).loc[lambda df: df["class_code"] == 3].iloc[0]["area_km2"] if m19 is not None else 121.6
                w25 = calculate_class_areas(m25, total_reference_area_km2=4054.0).loc[lambda df: df["class_code"] == 3].iloc[0]["area_km2"] if m25 is not None else 121.6
                w_diff = w25 - w19

                st.markdown(
                    f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:6px;">
                        <h4 style="margin:0 0 10px 0; color:#1e293b;">Key Water Body Findings (2019–2025 Historical)</h4>
                        <ul style="font-size:13.5px; color:#475569; line-height:1.6; margin:0; padding-left:20px;">
                            <li><strong>Acreage Preservation:</strong> Permanent surface water extent has remained highly conserved across Azamgarh at exactly <strong>{w25:,.1f} km² ({water_pct:.1f}%)</strong> (net change: {w_diff:+.1f} km²).</li>
                            <li><strong>Tamsa River Meanders:</strong> The central course of the Tamsa River and its oxbow wetlands maintain consistent water presence across seasons.</li>
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

    # Dedicated 2025 vs 2030 Comparison Section (Part 3)
    map_2025 = maps.get(2025, {}).get("data")
    map_2030 = maps.get(2030, {}).get("data")
    if map_2025 is not None and map_2030 is not None:
        render_category_comparison_section(
            class_code=3,
            map_2025=map_2025,
            map_2030=map_2030,
            is_synthetic=maps.get(2030, {}).get("is_synthetic", True),
        )

    # 5-Class Legend Cards at bottom
    st.markdown("---")
    render_legend_cards(header="🏷️ 5-Class Legend")


if __name__ == "__main__":
    render_water_page()
