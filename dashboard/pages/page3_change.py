"""Page 3: Historical Change Analysis, Gains/Losses, and Hotspots."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.data_loader import (
    CLASS_COLORS,
    CLASS_NAMES,
    is_demo_mode,
    load_available_raster_maps,
)
from src.analysis.area_stats import calculate_class_areas, calculate_gain_loss
from src.analysis.change_detection import (
    detect_land_cover_changes,
    extract_critical_transitions,
    identify_change_hotspots,
)
from src.models.prediction import calculate_transition_matrix


def render_change_page():
    st.markdown('<div class="page-title">📈 Past-versus-Present Change Detection & Transition Dynamics</div>', unsafe_allow_html=True)
    st.markdown("Quantify land-use transformations, urban encroachment into fertile cropland, gains/losses in square kilometres and hectares, and spatial conversion hotspots.")

    if is_demo_mode():
        st.warning(
            "⚠️ **DEMO / SYNTHETIC DATA NOTICE — NOT VALIDATED SATELLITE FINDINGS**\n\n"
            "The change detection metrics, transition cross-tabulations, and hotspot maps below are computed from synthetic test rasters. "
            "They serve as an end-to-end demonstration of the analytical methodology. "
            "To evaluate authentic historical change dynamics across Azamgarh, authenticate Earth Engine and run `python src/pipeline.py --mode live`."
        )

    maps = load_available_raster_maps()
    available_years = sorted(maps.keys())

    if len(available_years) < 2:
        st.warning("At least two classified maps are required to compute change detection.")
        return

    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        y1 = st.selectbox("Baseline Year (T1):", available_years, index=0)
    with c2:
        y2 = st.selectbox("Comparison Year (T2):", available_years, index=len(available_years) - 1)
    with c3:
        st.markdown(f"**Period:** `{y1} → {y2}` ({y2 - y1} Years)")
        st.caption("Pixel Size: 20 m resampled grid | Total Conserved Area: 4,054.0 km²")

    if y1 >= y2:
        st.error("Baseline year T1 must be strictly earlier than comparison year T2.")
        return

    map1 = maps[y1]["data"]
    map2 = maps[y2]["data"]

    # Calculate area statistics for both years
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
    st.markdown("### 🗺️ Side-by-Side Map Comparison")
    col_map_t1, col_map_t2 = st.columns(2)
    with col_map_t1:
        st.markdown(f"#### 📅 Baseline Year: {y1}")
        fig_t1 = px.imshow(map1, color_continuous_scale=color_scale, range_color=[1, 5], aspect="equal")
        fig_t1.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=380, coloraxis_showscale=False)
        st.plotly_chart(fig_t1, use_container_width=True)
        st.caption(f"Figure: LULC Classification Map for Azamgarh ({y1})")

    with col_map_t2:
        st.markdown(f"#### 📅 Comparison Year: {y2}")
        fig_t2 = px.imshow(map2, color_continuous_scale=color_scale, range_color=[1, 5], aspect="equal")
        fig_t2.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=380, coloraxis_showscale=False)
        st.plotly_chart(fig_t2, use_container_width=True)
        st.caption(f"Figure: LULC Classification Map for Azamgarh ({y2})")

    st.markdown("---")

    # 1. Gain / Loss Bar Chart
    st.subheader(f"📊 Net Land Cover Change ({y1} → {y2})")

    fig_gl = go.Figure()
    colors = [
        "#2E7D32" if val > 0 else "#D32F2F" for val in gain_loss_df["abs_change_km2"]
    ]
    fig_gl.add_trace(go.Bar(
        x=gain_loss_df["class_name"],
        y=gain_loss_df["abs_change_km2"],
        marker_color=colors,
        text=gain_loss_df.apply(lambda r: f"{r['abs_change_km2']:+.1f} km² ({r['abs_change_ha']:+.0f} ha)", axis=1),
        textposition="auto",
    ))
    fig_gl.update_layout(
        yaxis_title="Net Change (km²)",
        xaxis_title="Land Cover Class",
        margin=dict(l=20, r=20, t=20, b=20),
        height=320,
    )
    st.plotly_chart(fig_gl, use_container_width=True)

    # 2. Detailed Gain/Loss Table (km² and Hectares)
    st.markdown("#### 📋 Class Area Comparison and Percentage Change")
    st.dataframe(
        gain_loss_df[[
            "class_name", f"area_km2_{y1}", f"area_ha_{y1}", f"percentage_{y1}",
            f"area_km2_{y2}", f"area_ha_{y2}", f"percentage_{y2}",
            "abs_change_km2", "abs_change_ha", "pct_pt_change", "trend"
        ]].rename(columns={
            "class_name": "Class",
            f"area_km2_{y1}": f"Area {y1} (km²)",
            f"area_ha_{y1}": f"Area {y1} (ha)",
            f"percentage_{y1}": f"Share {y1} (%)",
            f"area_km2_{y2}": f"Area {y2} (km²)",
            f"area_ha_{y2}": f"Area {y2} (ha)",
            f"percentage_{y2}": f"Share {y2} (%)",
            "abs_change_km2": "Net Δ (km²)",
            "abs_change_ha": "Net Δ (ha)",
            "pct_pt_change": "Δ Share (% pts)",
            "trend": "Trend",
        }),
        use_container_width=True,
    )

    st.markdown("---")

    # 3. Class-to-Class Transition Matrix
    st.subheader(f"🔄 Class-to-Class Transition Matrix ({y1} → {y2})")
    count_df, prob_df = calculate_transition_matrix(map1, map2)

    t_tab1, t_tab2 = st.tabs(["📊 Transition Probabilities ($P_{ij}$)", "🔢 Absolute Pixel Transitions (Counts)"])
    with t_tab1:
        st.markdown(f"**Empirical Transition Probability Matrix ($P_{{ij}}$ from {y1} to {y2}):**")
        st.dataframe(prob_df.style.format("{:.4f}").background_gradient(cmap="Blues"), use_container_width=True)
    with t_tab2:
        st.markdown(f"**Cross-Tabulation Matrix (Pixel Counts from {y1} to {y2}):**")
        st.dataframe(count_df, use_container_width=True)

    st.markdown("---")

    # 4. Critical Transitions and Urban Expansion
    st.subheader("🏙️ Critical Socio-Ecological Transitions")
    change_mask, trans_df = detect_land_cover_changes(map1, map2)
    crit_df = extract_critical_transitions(trans_df, total_reference_area_km2=4054.0)

    col_tr_left, col_tr_right = st.columns([3, 2])
    with col_tr_left:
        st.markdown("**Top Observed Transitions (Ranked by Extent):**")
        st.dataframe(
            crit_df[["transition_label", "estimated_area_km2", "estimated_area_ha", "pct_of_landscape"]].head(8).rename(columns={
                "transition_label": "Transition Path",
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

        st.markdown(f"""
        <div style="background:#fff3e0; border-left: 4px solid #f57c00; padding: 12px; border-radius: 4px;">
            <h4 style="margin:0 0 8px 0; color:#e65100;">Cropland-to-Built-up Conversion</h4>
            <p style="margin:0; font-size:14px;">Between {y1} and {y2}, an estimated <strong>{agri_loss_km2:.1f} km²</strong> (<strong>{agri_loss_ha:,.0f} hectares</strong>) of agricultural land was converted into built-up and settlement surfaces, primarily along radial transit arteries and the peri-urban fringe of Azamgarh City.</p>
        </div>
        """, unsafe_allow_html=True)

    # 5. Spatial Change Hotspot Map
    st.markdown("---")
    st.subheader("🔥 Spatial Change Hotspots")
    st.caption("Change density estimated using a 15-pixel (~300 m) spatial moving window.")

    density_grid, hotspot_mask = identify_change_hotspots(change_mask, kernel_size=15, hotspot_threshold_pct=20.0)

    fig_hs = px.imshow(
        density_grid,
        color_continuous_scale="Viridis",
        labels=dict(color="Change Density (%)"),
        aspect="equal",
    )
    fig_hs.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=480,
    )
    st.plotly_chart(fig_hs, use_container_width=True)

    # Legend
    st.markdown("---")
    st.markdown("### 🏷️ Standardized 5-Class Legend")
    l_cols = st.columns(5)
    for idx, c in enumerate([1, 2, 3, 4, 5]):
        with l_cols[idx]:
            st.markdown(
                f'<div style="background-color: {CLASS_COLORS[c]}; color: {"#000" if c in [1,5] else "#fff"}; '
                f'padding: 8px; border-radius: 6px; font-weight: bold; text-align: center; margin-bottom: 6px;">'
                f'Class {c}: {CLASS_NAMES[c]}</div>',
                unsafe_allow_html=True,
            )
