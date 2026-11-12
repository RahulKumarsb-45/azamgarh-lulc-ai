"""Page: Barren & Open Land Analysis for Azamgarh District."""
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
        available_years = [2019, 2022, 2025, 2030]

    # Period and Year Selector (Past, Present 2026, Future 2030)
    period_type, sel_year = render_period_and_year_selector("barren", available_years)

    if period_type == "present":
        # 2026 is not available offline; display clear, honest notice
        render_2026_unavailable_banner("Barren & Open Land", "🏜️")
    else:
        # Get data for selected year
        raster_data = maps.get(sel_year, {}).get("data")
        is_synthetic = maps.get(sel_year, {}).get("is_synthetic", True)

        if raster_data is None:
            st.info(f"Classification map for {sel_year} is currently unavailable.")
        else:
            # Calculate dynamic areas
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
            delta_label = "Change from 2019" if sel_year != 2019 else "Baseline Year"
            s3.metric(delta_label, f"{delta_km2:+.1f} km²")
            s4.metric("Primary Features", "Floodplain Sand & Bare Soil")

            st.markdown("---")

            # Visualizations: Map & Trend Chart
            col_map, col_trend = st.columns([3, 2])

            with col_map:
                year_label = f"{sel_year} (Predicted)" if period_type == "future" else str(sel_year)
                st.subheader(f"🗺️ Barren Land Distribution Map ({year_label})")
                render_category_map(
                    raster_data=raster_data,
                    class_code=5,
                    year=year_label,
                    is_synthetic=is_synthetic,
                    height=440,
                )

            with col_trend:
                st.subheader("📈 Multi-Year Barren Land Trend")
                trend_years = [y for y in [2019, 2022, 2025, 2030] if y in maps]
                trend_records = []
                for yr in trend_years:
                    d = calculate_class_areas(maps[yr]["data"], total_reference_area_km2=4054.0)
                    row = d[d["class_code"] == 5].iloc[0]
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
                        marker_color=CLASS_COLORS[5],
                        text=[f"{v:.0f} km²" for v in trend_df["Area_km2"]],
                        textposition="auto",
                    )
                )
                fig_trend.update_layout(
                    yaxis_title="Barren Area (km²)",
                    xaxis_title="Observation Year (* = Projected)",
                    margin=dict(l=10, r=10, t=20, b=10),
                    height=370,
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#f8fafc",
                )
                st.plotly_chart(fig_trend, use_container_width=True)

            # Detailed Findings / Characteristics
            st.markdown("---")
            st.subheader("🔍 Land Surface Stability & Soil Dynamics")

            c_f1, c_f2 = st.columns([3, 2])
            with c_f1:
                # Dynamic historical figures
                m19 = maps.get(2019, {}).get("data")
                m25 = maps.get(2025, {}).get("data")
                bar19 = calculate_class_areas(m19, total_reference_area_km2=4054.0).loc[lambda df: df["class_code"] == 5].iloc[0]["area_km2"] if m19 is not None else 91.2
                bar25 = calculate_class_areas(m25, total_reference_area_km2=4054.0).loc[lambda df: df["class_code"] == 5].iloc[0]["area_km2"] if m25 is not None else 91.2
                bar_diff = bar25 - bar19

                st.markdown(
                    f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:6px;">
                        <h4 style="margin:0 0 10px 0; color:#1e293b;">Key Barren Land Findings (2019–2025 Historical)</h4>
                        <ul style="font-size:13.5px; color:#475569; line-height:1.6; margin:0; padding-left:20px;">
                            <li><strong>Stable Baseline:</strong> Barren and open land extent remained consistent at <strong>{bar25:,.1f} km² ({barren_pct:.1f}%)</strong> (net change: {bar_diff:+.1f} km²).</li>
                            <li><strong>Dynamic Transition Buffer:</strong> Open ground acts as an intermediate stage between agricultural land clearing and final masonry construction.</li>
                            <li><strong>Fluvial Sandbars:</strong> Significant sandy stretches exist along the Ghaghara riverbed in Sagri tehsil, shifting with seasonal monsoon flood deposition.</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c_f2:
                st.markdown(
                    """
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:6px;">
                        <h4 style="margin:0 0 10px 0; color:#1e293b;">Soil & Surface Types</h4>
                        <p style="font-size:13px; color:#475569; line-height:1.5; margin:0;">
                            • <strong>Active Brick Kilns:</strong> Stripped topsoil pits located across rural outskirts.<br>
                            • <strong>Riverine Sands:</strong> High-reflectance sandy deposits along Ghaghara & Tamsa.<br>
                            • <strong>Transition Fallow:</strong> Uncultivated land awaiting construction.
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
            class_code=5,
            map_2025=map_2025,
            map_2030=map_2030,
            is_synthetic=maps.get(2030, {}).get("is_synthetic", True),
        )

    # 5-Class Legend Cards at bottom
    st.markdown("---")
    render_legend_cards(header="🏷️ 5-Class Legend")


if __name__ == "__main__":
    render_barren_page()
