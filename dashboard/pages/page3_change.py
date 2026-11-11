"""Page 3: Land Cover Change Detection and Transition Dynamics."""
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
    render_legend_cards,
    render_sidebar,
)
from src.analysis.area_stats import calculate_class_areas, calculate_gain_loss
from src.analysis.change_detection import (
    detect_land_cover_changes,
    extract_critical_transitions,
    identify_change_hotspots,
)
from src.models.prediction import calculate_transition_matrix


def render_change_page():
    render_sidebar()
    st.markdown('<div class="page-title">📈 Change Detection</div>', unsafe_allow_html=True)
    st.markdown("Analyze how Agriculture, Vegetation, Water Bodies, Built-up, and Barren Land have changed across Azamgarh District over time.")

    maps = load_available_raster_maps()
    available_years = sorted(maps.keys())

    if len(available_years) < 2:
        st.info("At least two classified maps are required to analyze land cover changes.")
        return

    # Year selection controls
    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        y1 = st.selectbox("Baseline Year (Start):", available_years, index=0)
    with c2:
        y2 = st.selectbox("Comparison Year (End):", available_years, index=len(available_years) - 1)
    with c3:
        st.markdown(f"**Selected Interval:** **{y1} → {y2}** ({y2 - y1} years)")
        st.caption("Total District Study Area: 4,054.0 km²")

    if y1 >= y2:
        st.error("The start year must be earlier than the end year. Please choose two different years.")
        return

    map1 = maps[y1]["data"]
    map2 = maps[y2]["data"]

    # Calculate statistics
    df_t1 = calculate_class_areas(map1, total_reference_area_km2=4054.0)
    df_t2 = calculate_class_areas(map2, total_reference_area_km2=4054.0)
    gain_loss_df = calculate_gain_loss(df_t1, df_t2, y1, y2)

    color_scale = [
        [0.0, CLASS_COLORS[1]], [0.2, CLASS_COLORS[1]],
        [0.2, CLASS_COLORS[2]], [0.4, CLASS_COLORS[2]],
        [0.4, CLASS_COLORS[3]], [0.6, CLASS_COLORS[3]],
        [0.6, CLASS_COLORS[4]], [0.8, CLASS_COLORS[4]],
        [0.8, CLASS_COLORS[5]], [1.0, CLASS_COLORS[5]],
    ]

    # Side-by-Side Map Comparison
    st.markdown("### 🗺️ Visual Map Comparison")
    col_map_t1, col_map_t2 = st.columns(2)
    with col_map_t1:
        st.markdown(f"#### 📅 Start Year: {y1}")
        fig_t1 = px.imshow(map1, color_continuous_scale=color_scale, range_color=[1, 5], aspect="equal")
        fig_t1.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=380, coloraxis_showscale=False)
        st.plotly_chart(fig_t1, use_container_width=True)

    with col_map_t2:
        st.markdown(f"#### 📅 End Year: {y2}")
        fig_t2 = px.imshow(map2, color_continuous_scale=color_scale, range_color=[1, 5], aspect="equal")
        fig_t2.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=380, coloraxis_showscale=False)
        st.plotly_chart(fig_t2, use_container_width=True)

    st.markdown("---")

    # 1. Gain / Loss Bar Chart
    st.subheader(f"📊 Net Land Cover Change ({y1} → {y2})")

    fig_gl = go.Figure()
    bar_colors = ["#2E7D32" if val >= 0 else "#D32F2F" for val in gain_loss_df["abs_change_km2"]]
    fig_gl.add_trace(
        go.Bar(
            x=[f"{CLASS_ICONS.get(idx + 1, '')} {name}" for idx, name in enumerate(gain_loss_df["class_name"])],
            y=gain_loss_df["abs_change_km2"],
            marker_color=bar_colors,
            text=gain_loss_df.apply(lambda r: f"{r['abs_change_km2']:+.1f} km²", axis=1),
            textposition="auto",
        )
    )
    fig_gl.update_layout(
        yaxis_title="Net Change (km²)",
        xaxis_title="Land Cover Category",
        margin=dict(l=20, r=20, t=20, b=20),
        height=320,
    )
    st.plotly_chart(fig_gl, use_container_width=True)

    # 2. Detailed Change Table
    st.markdown("#### 📋 Class Area Changes")
    st.dataframe(
        gain_loss_df[[
            "class_name", f"area_km2_{y1}", f"percentage_{y1}",
            f"area_km2_{y2}", f"percentage_{y2}",
            "abs_change_km2", "abs_change_ha", "pct_pt_change", "trend"
        ]].rename(columns={
            "class_name": "Category",
            f"area_km2_{y1}": f"Area {y1} (km²)",
            f"percentage_{y1}": f"Share {y1} (%)",
            f"area_km2_{y2}": f"Area {y2} (km²)",
            f"percentage_{y2}": f"Share {y2} (%)",
            "abs_change_km2": "Net Change (km²)",
            "abs_change_ha": "Net Change (Hectares)",
            "pct_pt_change": "Change (% pts)",
            "trend": "Trend",
        }),
        use_container_width=True,
    )

    st.markdown("---")

    # 3. Critical Land Conversions & Urban Expansion
    st.subheader("🏙️ Key Land Conversions")
    change_mask, trans_df = detect_land_cover_changes(map1, map2)
    crit_df = extract_critical_transitions(trans_df, total_reference_area_km2=4054.0)

    col_tr_left, col_tr_right = st.columns([3, 2])
    with col_tr_left:
        st.markdown("**Top Observed Land Conversions:**")
        st.dataframe(
            crit_df[["transition_label", "estimated_area_km2", "estimated_area_ha", "pct_of_landscape"]].head(6).rename(columns={
                "transition_label": "Conversion Path",
                "estimated_area_km2": "Extent (km²)",
                "estimated_area_ha": "Extent (ha)",
                "pct_of_landscape": "% of District",
            }),
            use_container_width=True,
        )

    with col_tr_right:
        urban_growth = crit_df[crit_df["to_code"] == 4]
        agri_to_urban = urban_growth[urban_growth["from_code"] == 1]
        agri_loss_km2 = agri_to_urban["estimated_area_km2"].sum() if not agri_to_urban.empty else 0.0
        agri_loss_ha = agri_to_urban["estimated_area_ha"].sum() if not agri_to_urban.empty else 0.0

        st.markdown(
            f"""
            <div style="background:#f8fafc; border:1px solid #cbd5e1; border-left: 4px solid #2e7d32; padding: 16px; border-radius: 6px;">
                <h4 style="margin:0 0 8px 0; color:#1e293b;">Urban Growth from Agriculture</h4>
                <p style="margin:0; font-size:14px; color:#475569; line-height:1.5;">
                    Between {y1} and {y2}, an estimated <strong>{agri_loss_km2:.1f} km²</strong> (<strong>{agri_loss_ha:,.0f} hectares</strong>)
                    of cultivated cropland was converted into built-up and settlement surfaces, primarily along major transit corridors and expanding town fringes.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 4. Spatial Change Hotspot Map
    st.markdown("---")
    st.subheader("🔥 Spatial Change Hotspots")
    st.caption("Areas with concentrated land cover alterations (computed across a local spatial neighborhood).")

    density_grid, _ = identify_change_hotspots(change_mask, kernel_size=15, hotspot_threshold_pct=20.0)

    fig_hs = px.imshow(
        density_grid,
        color_continuous_scale="Viridis",
        labels=dict(color="Change Intensity (%)"),
        aspect="equal",
    )
    fig_hs.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=460,
    )
    st.plotly_chart(fig_hs, use_container_width=True)

    # 5. Transition Probabilities (Simplified)
    with st.expander("🔍 View Detailed Transition Probability Table"):
        _, prob_df = calculate_transition_matrix(map1, map2)
        st.markdown(f"**Likelihood of category transitions from {y1} to {y2}:**")
        st.dataframe(prob_df.style.format("{:.3f}").background_gradient(cmap="Blues"), use_container_width=True)

    # Legend
    st.markdown("---")
    render_legend_cards(header="🏷️ 5-Class Legend")


if __name__ == "__main__":
    render_change_page()
