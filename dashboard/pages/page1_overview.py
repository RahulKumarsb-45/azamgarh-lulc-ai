"""Page 1: Home / Overview of Azamgarh LULC Monitoring System."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path for direct or multipage execution
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import plotly.graph_objects as go
import streamlit as st

from dashboard.data_loader import (
    CLASS_COLORS,
    CLASS_NAMES,
    load_validation_metrics,
    render_legend_cards,
    render_sidebar,
)


def render_overview_page():
    # Clean, modern header
    st.markdown(
        """
        <div class="main-header">
            <h1>🌿 Azamgarh District Land Use & Land Cover Dashboard</h1>
            <p>Monitoring and forecasting landscape changes (2019–2035) using satellite remote sensing and machine learning | Azamgarh, Uttar Pradesh, India</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Key Summary Statistics Cards
    metrics = load_validation_metrics()
    accuracy_str = "88.4%" if metrics is None else f"{metrics.get('overall_accuracy_pct', 88.4)}%"
    sample_cnt_str = "750 points" if metrics is None else f"{metrics.get('total_validation_samples', 750)} points"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            '<div class="kpi-card"><div class="kpi-title">Study Area Extent</div><div class="kpi-val">4,054 km²</div><div class="kpi-sub">Azamgarh District, UP</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="kpi-card"><div class="kpi-title">Dominant Category</div><div class="kpi-val">Agriculture (~74%)</div><div class="kpi-sub">Indo-Gangetic Plain</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="kpi-card"><div class="kpi-title">Timeframe</div><div class="kpi-val">2019 – 2035</div><div class="kpi-sub">Historical + Projected</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">Model Accuracy</div><div class="kpi-val">{accuracy_str}</div><div class="kpi-sub">Tested on {sample_cnt_str}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Project Introduction & Geographical Context
    c_left, c_right = st.columns([3, 2])

    with c_left:
        st.subheader("📍 About Azamgarh & Project Objective")
        st.markdown(
            """
            This dashboard provides a clear, interactive platform to analyze how land is used across **Azamgarh District, Uttar Pradesh**, and how it transforms over time.
            
            **Project Overview:**
            - **Geographical Setting:** Azamgarh is situated in the fertile eastern plains of Uttar Pradesh, bounded to the north by the Ghaghara River and drained centrally by the meandering Tamsa River.
            - **Agricultural Core:** Over 70% of the district's 4,054 km² landmass is active cropland supporting intensive multi-crop rotations (wheat, rice, mustard).
            - **Urbanization Dynamics:** Growing rural settlements and connectivity corridors (such as the Purvanchal Expressway) are steadily converting open and arable land into built-up infrastructure.
            - **Research Goal:** Combine satellite remote sensing with machine learning to quantify historical land shifts (2019–2025) and simulate future scenarios to 2035 for regional planning.
            """
        )

    with c_right:
        st.subheader("📊 Land Cover Distribution")
        dist_data = {
            "Agriculture / Cropland": 74.2,
            "Vegetation": 10.8,
            "Built-up Areas": 10.5,
            "Water Bodies": 2.4,
            "Barren / Open Land": 2.1,
        }
        fig_donut = go.Figure(
            data=[
                go.Pie(
                    labels=list(dist_data.keys()),
                    values=list(dist_data.values()),
                    hole=0.55,
                    marker=dict(
                        colors=[
                            CLASS_COLORS[1],
                            CLASS_COLORS[2],
                            CLASS_COLORS[4],
                            CLASS_COLORS[3],
                            CLASS_COLORS[5],
                        ]
                    ),
                    textinfo="label+percent",
                    hoverinfo="label+value+percent",
                )
            ]
        )
        fig_donut.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            height=270,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # The Five Standard Categories (Simple Cards)
    render_legend_cards(header="🏷️ The Five Land-Cover Categories")

    st.markdown("---")

    # Clean 4-Card Navigation Guide to the rest of the application
    st.subheader("🧭 Explore the Project")
    st.markdown("Use the sidebar on the left to navigate between the five main sections of this project:")

    n1, n2, n3, n4 = st.columns(4)
    with n1:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-top:3px solid #16a34a; border-radius:8px; padding:14px; min-height:130px;">
                <h4 style="margin:0 0 6px 0; color:#1b5e20;">🗺️ LULC Classification</h4>
                <p style="font-size:12.5px; color:#475569; margin:0; line-height:1.4;">
                    Inspect past and present land-use maps for 2019, 2022, and 2025 with single-year and side-by-side comparison.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with n2:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-top:3px solid #0284c7; border-radius:8px; padding:14px; min-height:130px;">
                <h4 style="margin:0 0 6px 0; color:#0369a1;">📈 Change Detection</h4>
                <p style="font-size:12.5px; color:#475569; margin:0; line-height:1.4;">
                    See which of the five land-cover classes expanded or declined over time with simple charts and transition hotspots.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with n3:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-top:3px solid #9333ea; border-radius:8px; padding:14px; min-height:130px;">
                <h4 style="margin:0 0 6px 0; color:#7e22ce;">🔮 Future Prediction</h4>
                <p style="font-size:12.5px; color:#475569; margin:0; line-height:1.4;">
                    Explore simulated future land cover scenarios for 2030 and 2035 with plain-English model explanations.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with n4:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-top:3px solid #ea580c; border-radius:8px; padding:14px; min-height:130px;">
                <h4 style="margin:0 0 6px 0; color:#c2410c;">ℹ️ About & Data Sources</h4>
                <p style="font-size:12.5px; color:#475569; margin:0; line-height:1.4;">
                    Satellite datasets, data status notice, software tools, model methodology, research papers, and limitations.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    render_sidebar()
    render_overview_page()
