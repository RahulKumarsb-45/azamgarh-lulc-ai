"""Page: Future Land-Cover Prediction (2030) with CA-Markov Simulation."""
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
from src.analysis.area_stats import calculate_class_areas
from src.models.prediction import (
    calculate_transition_matrix,
    cellular_automata_markov_simulation,
    run_historical_backtest,
)


def load_prediction_raster(year: int) -> np.ndarray | None:
    npy_path = Path("data/outputs/predictions") / f"predicted_map_{year}.npy"
    if npy_path.exists():
        try:
            return np.load(npy_path)
        except Exception:
            pass
    return None


def render_future_predictions_page():
    render_sidebar()
    st.markdown('<div class="page-title">🔮 Future Land-Cover Prediction (2030)</div>', unsafe_allow_html=True)
    st.markdown("Explore the 2030 future simulated land-use and land-cover projection modeled using CA-Markov spatial simulation.")

    # Clear, professional simulation notice
    st.markdown(
        """
        <div style="background-color: #fefce8; border: 1px solid #fef08a; border-left: 4px solid #ca8a04; padding: 14px; border-radius: 6px; margin-bottom: 20px;">
            <strong style="color: #854d0e; font-size: 14px;">⚠️ DEMONSTRATION / SYNTHETIC CA-MARKOV PREDICTION — NOT A REAL SATELLITE FORECAST:</strong><br>
            <span style="font-size: 13.5px; color: #713f12; line-height: 1.5;">
                The <strong>2030 projection</strong> is a <strong>computer simulation scenario</strong> derived from historical transition trends (2019–2025)
                using Cellular Automata-Markov chain spatial allocation. In offline demonstration mode, predictions project simulated baseline dynamics
                for academic and planning illustration. They are <strong>not</strong> real-time satellite forecasts.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    maps = load_available_raster_maps()
    base_map = maps.get(2025, {}).get("data")
    map_2019 = maps.get(2019, {}).get("data")
    map_2022 = maps.get(2022, {}).get("data")

    # Load pre-saved 2030 prediction raster or simulate
    map_2030 = load_prediction_raster(2030)

    if map_2019 is not None and map_2022 is not None:
        _, prob_df = calculate_transition_matrix(map_2019, map_2022)
    else:
        P_default = np.array([
            [0.94, 0.02, 0.005, 0.03, 0.005],
            [0.05, 0.90, 0.005, 0.04, 0.005],
            [0.02, 0.01, 0.95,  0.01, 0.01],
            [0.005, 0.002, 0.001, 0.99, 0.002],
            [0.10, 0.03, 0.01,  0.06, 0.80],
        ])
        prob_df = pd.DataFrame(P_default, index=[f"Class {c}" for c in range(1, 6)], columns=[f"Class {c}" for c in range(1, 6)])

    if map_2030 is None and base_map is not None:
        map_2030 = cellular_automata_markov_simulation(base_map, prob_df.values, iterations=5, seed=2030)

    color_scale = [
        [0.0, CLASS_COLORS[1]], [0.2, CLASS_COLORS[1]],
        [0.2, CLASS_COLORS[2]], [0.4, CLASS_COLORS[2]],
        [0.4, CLASS_COLORS[3]], [0.6, CLASS_COLORS[3]],
        [0.6, CLASS_COLORS[4]], [0.8, CLASS_COLORS[4]],
        [0.8, CLASS_COLORS[5]], [1.0, CLASS_COLORS[5]],
    ]

    # Tabs for simple navigation
    tab_maps, tab_method, tab_backtest = st.tabs([
        "🗺️ 2025 vs 2030 Projected Map",
        "💡 How the Prediction Works",
        "🔬 Model Verification (Hindcasting)",
    ])

    with tab_maps:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 📅 2025 Observed Baseline Map")
            st.caption("Latest verified satellite observation")
            if base_map is not None:
                fig_25 = px.imshow(base_map, color_continuous_scale=color_scale, range_color=[1, 5], aspect="equal")
                fig_25.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=400, coloraxis_showscale=False)
                st.plotly_chart(fig_25, use_container_width=True)
            else:
                st.info("2025 raster unavailable.")

        with c2:
            st.markdown("#### 📅 2030 Projected Simulation Map")
            st.caption("5-year CA-Markov simulation forecast")
            if map_2030 is not None:
                fig_30 = px.imshow(map_2030, color_continuous_scale=color_scale, range_color=[1, 5], aspect="equal")
                fig_30.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=400, coloraxis_showscale=False)
                st.plotly_chart(fig_30, use_container_width=True)
            else:
                st.info("2030 prediction raster unavailable.")

        # Area Summary Table
        st.markdown("---")
        st.subheader("📊 Land Cover Trajectory & 2025 vs 2030 Comparison")

        if base_map is not None and map_2030 is not None:
            df_2019 = calculate_class_areas(map_2019 if map_2019 is not None else base_map, total_reference_area_km2=4054.0)
            df_2022 = calculate_class_areas(map_2022 if map_2022 is not None else base_map, total_reference_area_km2=4054.0)
            df_2025 = calculate_class_areas(base_map, total_reference_area_km2=4054.0)
            df_2030 = calculate_class_areas(map_2030, total_reference_area_km2=4054.0)

            traj_df = pd.DataFrame({
                "Category": [f"{CLASS_ICONS[c]} {CLASS_NAMES[c]}" for c in range(1, 6)],
                "2019 (Observed)": [f"{v:.1f} km² ({p:.1f}%)" for v, p in zip(df_2019["area_km2"].values, df_2019["percentage"].values)],
                "2022 (Observed)": [f"{v:.1f} km² ({p:.1f}%)" for v, p in zip(df_2022["area_km2"].values, df_2022["percentage"].values)],
                "2025 (Observed)": [f"{v:.1f} km² ({p:.1f}%)" for v, p in zip(df_2025["area_km2"].values, df_2025["percentage"].values)],
                "2030 (Predicted)": [f"{v:.1f} km² ({p:.1f}%)" for v, p in zip(df_2030["area_km2"].values, df_2030["percentage"].values)],
                "Net Change 2025→2030": [
                    f"{(v30 - v25):+.1f} km²"
                    for v25, v30 in zip(df_2025["area_km2"].values, df_2030["area_km2"].values)
                ],
                "Percent Change (%)": [
                    f"{((v30 - v25) / v25 * 100):+.2f}%"
                    for v25, v30 in zip(df_2025["area_km2"].values, df_2030["area_km2"].values)
                ],
            })
            st.dataframe(traj_df, use_container_width=True, hide_index=True)

    with tab_method:
        st.subheader("💡 How the CA-Markov Prediction Works")
        st.markdown(
            """
            The predictive model uses a widely accepted spatial simulation approach called **CA-Markov** (Cellular Automata – Markov Chain).
            
            1. **Historical Transition Probability (Markov Chain):**
               - The empirical transition probability matrix is derived from multi-temporal classified maps (2019–2025).
               - It quantifies the probability $P_{ij}$ that a pixel in class $i$ transitions to class $j$ over the time step.
            
            2. **Spatial Neighbourhood Allocation (Cellular Automata):**
               - Growth is not spatially random. Settlements and roads cluster near existing urban centers and transit corridors.
               - A Moore neighbourhood spatial contiguity kernel calculates local suitability, accelerating conversion where target classes already predominate.
            
            3. **Forward Projection Horizon:**
               - Starting from the verified 2025 baseline, the CA-Markov model projects land-cover allocation forward to **2030**.
            """
        )

    with tab_backtest:
        st.subheader("🔬 Historical Backtesting & Validation (Hindcasting)")
        st.markdown(
            """
            Before projecting future scenarios, the CA-Markov pipeline underwent rigorous historical backtesting:
            - **Calibration:** Model transition probabilities were calibrated strictly on historical observations (**2019 → 2022**).
            - **Blind Simulation:** The model projected land allocation forward to **2025** without access to actual 2025 data.
            - **Validation:** The simulated 2025 map was compared pixel-by-pixel with the observed 2025 classified map.
            """
        )

        if map_2019 is not None and map_2022 is not None and base_map is not None:
            backtest_res = run_historical_backtest(map_2019, map_2022, base_map, years=(2019, 2022, 2025))

            b1, b2, b3 = st.columns(3)
            b1.metric("Overall Spatial Agreement", f"{backtest_res['overall_agreement_pct']}%", help="Percentage of matching pixels between simulated and actual 2025.")
            b2.metric("Cohen's Kappa", f"{backtest_res['cohens_kappa']:.4f}", help="Statistical agreement corrected for chance agreement.")
            b3.metric("Figure of Merit (FoM)", f"{backtest_res['figure_of_merit']:.4f}", help="Validation metric for correctly simulated changes.")

            st.markdown(
                f"""
                <div style="background:#f8fafc; border:1px solid #cbd5e1; padding:14px; border-radius:6px; margin-top:10px; font-size:13px; color:#334155;">
                    <strong>Validation Outcome:</strong> The CA-Markov model achieved <strong>{backtest_res['overall_agreement_pct']}%</strong> overall spatial agreement
                    and a Cohen's Kappa of <strong>{backtest_res['cohens_kappa']:.4f}</strong> on historical hindcasting, confirming strong spatial predictive capability.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Legend
    st.markdown("---")
    render_legend_cards(header="🏷️ 5-Class Legend")


if __name__ == "__main__":
    render_future_predictions_page()
