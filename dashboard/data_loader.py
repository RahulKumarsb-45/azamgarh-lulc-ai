"""Data loader and cache manager for the Streamlit dashboard.

Separates data fetching from rendering, provides robust caching, and handles
missing or synthetic files gracefully without crashing.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st
import yaml
import plotly.graph_objects as go


CLASS_COLORS = {
    1: "#F2CF55",  # Agriculture / Cropland (Yellow)
    2: "#27833B",  # Vegetation (Green)
    3: "#2588D8",  # Water Bodies (Blue)
    4: "#D92F35",  # Built-up Areas (Red)
    5: "#A58B80",  # Barren / Open Land (Brown)
}

CLASS_NAMES = {
    1: "Agriculture / Cropland",
    2: "Vegetation",
    3: "Water Bodies",
    4: "Built-up Areas",
    5: "Barren / Open Land",
}

CLASS_ICONS = {
    1: "🌾",
    2: "🌳",
    3: "💧",
    4: "🏙️",
    5: "🏜️",
}

CLASS_DESCRIPTIONS = {
    1: "Wheat, paddy, mustard and other cultivated fields.",
    2: "Trees, orchards, green areas and vegetation cover.",
    3: "Rivers, lakes, ponds and irrigation channels.",
    4: "Buildings, houses, roads and urban settlements.",
    5: "Bare soil, unused land and open sandy areas.",
}

AZAMGARH_BBOX = [82.80, 25.70, 83.65, 26.35]
AZAMGARH_AREA_KM2 = 4054.0

CATEGORY_MAP_INSIGHTS = {
    1: {
        "shows": "Spatial distribution of active agricultural fields, crop fallow, and cultivated croplands across Azamgarh District.",
        "highlighted": "Agriculture / Cropland (highlighted in yellow, #F2CF55). All other land covers are muted.",
        "concentration": "Concentrated extensively across the fertile central, eastern, and southern alluvial plains of Azamgarh.",
        "trend": "Cultivated cropland decreased modestly from 2,920.1 km² (72.0%) in 2019 to 2,752.3 km² (67.9%) in 2025 (-167.8 km²), primarily driven by conversion to rural settlements and highway infrastructure.",
    },
    2: {
        "shows": "Spatial distribution of perennial tree canopies, horticultural orchards, and roadside green belts.",
        "highlighted": "Vegetation & Tree Cover (highlighted in green, #27833B). All other land covers are muted.",
        "concentration": "Concentrated in traditional village mango and guava orchards, riverine groves along the Tamsa River, and canal-side plantations.",
        "trend": "Maintained steady coverage around 410.3 km² (~10.1%), with localized tree felling for highway widening offset by mature village agroforestry.",
    },
    3: {
        "shows": "Spatial distribution of surface hydrology, including rivers, oxbow lakes, village ponds, and canal arteries.",
        "highlighted": "Water Bodies (highlighted in blue, #2588D8). All other land covers are muted.",
        "concentration": "Centered along the meanders of the Tamsa (Tons) River through central Azamgarh, the Ghaghara River along the northern border, and hundreds of village pokharis.",
        "trend": "Stable perennial surface water baseline of ~121.6 km² (~3.0%), with notable expansion during the post-monsoon season.",
    },
    4: {
        "shows": "Spatial distribution of masonry buildings, settlements, commercial zones, paved roadways, and impervious infrastructure.",
        "highlighted": "Built-up Areas & Settlements (highlighted in red, #D92F35). All other land covers are muted.",
        "concentration": "Clustered densely around Azamgarh Municipal City, key tehsil towns (Sagri, Lalganj, Phoolpur), and radial highway corridors including the Purvanchal Expressway.",
        "trend": "Rapid expansion from 510.8 km² (12.6%) in 2019 to 678.6 km² (16.7%) in 2025 (+167.8 km² / +32.9%), representing the primary driver of regional land transformation.",
    },
    5: {
        "shows": "Spatial distribution of uncultivated open ground, sandy riverbeds, brick-kiln clearings, and exposed soil parcels.",
        "highlighted": "Barren / Open Land (highlighted in brown, #A58B80). All other land covers are muted.",
        "concentration": "Fluvial sand deposits along the Ghaghara and Tamsa river channels, active brick kilns, and temporarily cleared land parcels awaiting construction.",
        "trend": "Stable baseline around 91.2 km² (~2.25%), fluctuating primarily with seasonal river discharges and cyclical construction preparation.",
    },
}


def render_category_map(
    raster_data: np.ndarray,
    class_code: int,
    year: int | str,
    is_synthetic: bool = True,
    height: int = 450,
) -> None:
    """Render a dedicated, consistent Azamgarh District map highlighting ONLY the selected class.

    Requirements addressed:
    - Verified boundary: Bbox [82.80, 25.70, 83.65, 26.35]
    - Dedicated class color highlighting, non-class areas muted/transparent
    - Interactive pan and zoom controls
    - Explanatory breakdown and honest demonstration data status notice
    """
    name = CLASS_NAMES.get(class_code, f"Class {class_code}")
    icon = CLASS_ICONS.get(class_code, "📍")
    color = CLASS_COLORS.get(class_code, "#2588D8")
    insights = CATEGORY_MAP_INSIGHTS.get(class_code, {})

    # Top header indicator
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:6px 12px;">
            <div>
                <span style="display:inline-block; width:14px; height:14px; background-color:{color}; border-radius:3px; vertical-align:middle; margin-right:6px;"></span>
                <strong style="color:#0f172a; font-size:13.5px;">{icon} {name} (Highlighted)</strong>
                <span style="color:#64748b; font-size:12px; margin-left:8px;">• Non-category areas muted</span>
            </div>
            <span style="font-size:11.5px; color:#475569; font-weight:600;">Azamgarh District BBox [82.80°–83.65°E, 25.70°–26.35°N]</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Prepare single-category mask
    mask = (raster_data == class_code).astype(int)
    H, W = raster_data.shape
    lons = np.linspace(82.80, 83.65, W)
    lats = np.linspace(26.35, 25.70, H)

    # Plotly heatmap with geographical coordinates and aspect ratio
    fig = go.Figure(
        data=go.Heatmap(
            z=mask,
            x=lons,
            y=lats,
            colorscale=[[0.0, "rgba(241, 245, 249, 0.85)"], [1.0, color]],
            showscale=False,
            hovertemplate=f"<b>{icon} {name}</b><br>Longitude: %{{x:.3f}}°E<br>Latitude: %{{y:.3f}}°N<extra></extra>",
        )
    )

    fig.update_layout(
        xaxis=dict(
            title="Longitude (°E)",
            range=[82.78, 83.67],
            showgrid=True,
            gridcolor="#e2e8f0",
            zeroline=False,
        ),
        yaxis=dict(
            title="Latitude (°N)",
            range=[25.68, 26.37],
            scaleanchor="x",
            scaleratio=1,
            showgrid=True,
            gridcolor="#e2e8f0",
            zeroline=False,
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8fafc",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Descriptive explanation below map
    st.markdown(
        f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-left:4px solid {color}; border-radius:6px; padding:12px 14px; margin-top:10px;">
            <div style="font-weight:700; color:#1e293b; font-size:13.5px; margin-bottom:6px;">📌 {icon} {name} — Spatial Distribution & Insights ({year})</div>
            <ul style="font-size:13px; color:#475569; line-height:1.55; margin:0; padding-left:18px;">
                <li><strong>Map Coverage:</strong> {insights.get('shows', '')}</li>
                <li><strong>Active Highlight:</strong> {insights.get('highlighted', '')}</li>
                <li><strong>Concentration Zone:</strong> {insights.get('concentration', '')}</li>
                <li><strong>Observed Trend (2019–2025):</strong> {insights.get('trend', '')}</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Honest data status notice
    if is_synthetic:
        st.markdown(
            """
            <div style="background:#fefce8; border:1px solid #fef08a; border-radius:6px; padding:8px 12px; margin-top:8px; font-size:12px; color:#854d0e;">
                <strong>⚠️ DEMONSTRATION / SYNTHETIC DATA:</strong> This map displays simulated spatial patterns for college demonstration. Real-time satellite validation requires active Google Earth Engine processing.
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar(active_category: int | str | None = None):
    """Render the simple, text-based project sidebar with zero images or map illustrations.
    
    Sidebar structure:
    1. College Project Demonstration badge
    2. Main Overview
    3. Land Cover Analysis heading
    4. Five category navigation options
    5. Study Area information
    6. Sensor information
    7. Model information
    8. Project footer
    + System Multipage Navigation (at bottom)
    """
    with st.sidebar:
        # 1. College Project Demonstration badge
        st.markdown('<span class="sidebar-badge">College Project Demonstration</span>', unsafe_allow_html=True)

        # 2. Main Overview
        st.page_link("app.py", label="Main Overview", icon="🏠")

        # 3. Land Cover Analysis heading
        st.markdown("### 📊 Land Cover Analysis")

        # 4. Five category navigation options (clean, simple, text-based)
        st.page_link("pages/page_agriculture.py", label="🌾 Agriculture Analysis")
        st.page_link("pages/page4_vegetation.py", label="🌳 Vegetation Analysis")
        st.page_link("pages/page_water.py", label="💧 Water Bodies Analysis")
        st.page_link("pages/page_builtup.py", label="🏙️ Built-up Area Analysis")
        st.page_link("pages/page_barren.py", label="🏜️ Barren / Open Land Analysis")

        # 5. Study Area information
        st.markdown("---")
        st.markdown("**📍 Study Area:** Azamgarh District, Uttar Pradesh")

        # 6. Sensor information
        st.markdown("**🛰️ Sensor:** Sentinel-2 Surface Reflectance")

        # 7. Model information
        st.markdown("**🤖 Model:** Random Forest + CA-Markov")

        # 8. Project footer
        st.markdown("---")
        st.caption("Azamgarh LULC System | Final Year CSE Project")

        # BOTTOM SECTION — Automatic Streamlit Page Navigation
        st.markdown("---")
        st.markdown("##### 📄 System Multipage Navigation")
        st.page_link("pages/page1_overview.py", label="page1 overview", icon="🏠")
        st.page_link("pages/page2_maps.py", label="page2 maps", icon="🗺️")
        st.page_link("pages/page3_change.py", label="page3 change", icon="📈")
        st.page_link("pages/page4_vegetation.py", label="page4 vegetation", icon="🌳")
        st.page_link("pages/page5_prediction.py", label="page5 prediction", icon="🔮")
        st.page_link("pages/page6_accuracy.py", label="page6 accuracy", icon="📊")
        st.page_link("pages/page8_documentation.py", label="page8 documentation", icon="ℹ️")


def render_legend_cards(header: str = "🏷️ Land Cover Classes"):
    """Render 5 simple, attractive, modern cards for the LULC categories."""
    if header:
        st.markdown(f"### {header}")
    cols = st.columns(5)
    for idx, c in enumerate([1, 2, 3, 4, 5]):
        with cols[idx]:
            color = CLASS_COLORS[c]
            icon = CLASS_ICONS[c]
            name = CLASS_NAMES[c]
            desc = CLASS_DESCRIPTIONS[c]
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 4px solid {color};
                            border-radius: 8px; padding: 12px 10px; margin-bottom: 8px; min-height: 110px;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                        <span style="font-size: 18px;">{icon}</span>
                        <span style="font-weight: 700; font-size: 13.5px; color: #1e293b;">{name}</span>
                    </div>
                    <div style="font-size: 12px; color: #64748b; line-height: 1.4;">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )



@st.cache_data
def load_class_schema() -> dict:
    """Load class schema configuration."""
    path = Path("config/class_schema.yaml")
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {"classes": {k: {"name": v, "color": CLASS_COLORS[k]} for k, v in CLASS_NAMES.items()}}


@st.cache_data
def load_settings() -> dict:
    """Load settings configuration."""
    path = Path("config/settings.yaml")
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


@st.cache_data
def load_audit_data() -> dict[str, Any]:
    """Load Phase 0 audit outputs if generated."""
    audit_dir = Path("data/outputs/audit")
    out = {
        "is_available": False,
        "boundary": None,
        "collection_ranges": None,
        "s2_audit": None,
        "landsat": None,
        "dynamic_world": None,
        "summary_md": "",
    }
    if not audit_dir.exists():
        return out

    b_file = audit_dir / "boundary_report.csv"
    if b_file.is_file():
        out["boundary"] = pd.read_csv(b_file)
        out["is_available"] = True

    c_file = audit_dir / "collection_ranges.csv"
    if c_file.is_file():
        out["collection_ranges"] = pd.read_csv(c_file)

    s2_file = audit_dir / "s2_year_season_audit.csv"
    if s2_file.is_file():
        out["s2_audit"] = pd.read_csv(s2_file)

    ls_file = audit_dir / "landsat_yearly.csv"
    if ls_file.is_file():
        out["landsat"] = pd.read_csv(ls_file)

    dw_file = audit_dir / "dynamicworld_yearly.csv"
    if dw_file.is_file():
        out["dynamic_world"] = pd.read_csv(dw_file)

    md_file = audit_dir / "audit_summary.md"
    if md_file.is_file():
        out["summary_md"] = md_file.read_text(encoding="utf-8")

    return out


@st.cache_data
def is_demo_mode() -> bool:
    """Check if system is operating in synthetic / demo mode."""
    prov_file = Path("data/outputs/provenance.json")
    if prov_file.is_file():
        try:
            with open(prov_file, "r", encoding="utf-8") as f:
                prov = json.load(f)
                return bool(prov.get("is_synthetic", True))
        except Exception:
            pass

    metrics_file = Path("data/outputs/metrics/accuracy_metrics.json")
    if metrics_file.is_file():
        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("is_synthetic", True))
        except Exception:
            pass
    return True


@st.cache_data
def load_available_raster_maps() -> dict[int | str, dict]:
    """Load classified raster maps (real or synthetic fallback) with accurate provenance tagging."""
    maps: dict[int | str, dict] = {}
    is_syn = is_demo_mode()

    # Check real outputs first
    real_dir = Path("data/outputs/classified")
    if real_dir.exists():
        for f in sorted(real_dir.glob("*.npy")):
            try:
                # Name pattern: lulc_map_2025.npy
                year_part = f.stem.split("_")[-1]
                year = int(year_part) if year_part.isdigit() else year_part
                data = np.load(f)
                maps[year] = {"data": data, "is_synthetic": is_syn, "source": f.name}
            except Exception:
                continue

    # Also check predictions
    pred_dir = Path("data/outputs/predictions")
    if pred_dir.exists():
        for f in sorted(pred_dir.glob("*.npy")):
            try:
                year_part = f.stem.split("_")[-1]
                year = int(year_part) if year_part.isdigit() else year_part
                data = np.load(f)
                maps[year] = {"data": data, "is_synthetic": is_syn, "source": f.name}
            except Exception:
                continue

    # Fallback to synthetic test fixtures if real outputs not yet generated
    if not maps:
        syn_dir = Path("data/synthetic_fixture")
        if syn_dir.exists():
            for f in sorted(syn_dir.glob("synthetic_map_*.npy")):
                try:
                    year_part = f.stem.split("_")[-1]
                    year = int(year_part) if year_part.isdigit() else year_part
                    data = np.load(f)
                    maps[year] = {"data": data, "is_synthetic": True, "source": f.name}
                except Exception:
                    continue

    return maps


@st.cache_data
def load_area_statistics() -> pd.DataFrame | None:
    """Load computed area statistics CSV if available."""
    candidates = [
        Path("data/outputs/change/class_area_summary.csv"),
        Path("data/outputs/classified/area_summary.csv"),
        Path("data/synthetic_fixture/synthetic_area_summary.csv"),
    ]
    for c in candidates:
        if c.is_file():
            return pd.read_csv(c)
    return None


@st.cache_data
def load_validation_metrics() -> dict | None:
    """Load model accuracy and validation metrics, attaching tabular class metrics."""
    candidates = [
        Path("data/outputs/metrics/accuracy_metrics.json"),
        Path("data/synthetic_fixture/synthetic_accuracy_metrics.json"),
    ]
    metrics = None
    for c in candidates:
        if c.is_file():
            try:
                with open(c, "r", encoding="utf-8") as f:
                    metrics = json.load(f)
                break
            except Exception:
                continue

    if metrics is None:
        return None

    # Attach per-class metrics DataFrame if available
    class_metrics_csv = Path("data/outputs/metrics/class_validation_metrics.csv")
    if class_metrics_csv.is_file():
        metrics["class_metrics"] = pd.read_csv(class_metrics_csv)
    elif "class_metrics" in metrics and isinstance(metrics["class_metrics"], list):
        metrics["class_metrics"] = pd.DataFrame(metrics["class_metrics"])

    # Attach Olofsson area-adjusted DataFrame if available
    olofsson_csv = Path("data/outputs/metrics/olofsson_adjusted_areas.csv")
    if olofsson_csv.is_file():
        metrics["olofsson_adjusted"] = pd.read_csv(olofsson_csv)

    return metrics


@st.cache_data
def load_backtest_results() -> dict | None:
    """Load historical backtest evaluation results."""
    candidates = [
        Path("data/outputs/metrics/backtest_results.json"),
        Path("data/synthetic_fixture/synthetic_backtest_results.json"),
    ]
    for c in candidates:
        if c.is_file():
            try:
                with open(c, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                continue
    return None
