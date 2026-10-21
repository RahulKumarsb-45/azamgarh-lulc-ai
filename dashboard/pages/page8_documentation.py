"""Page 8: Complete Project Tools, Data Sources, Image Provenance & Methodology Documentation."""
from __future__ import annotations

from pathlib import Path
import streamlit as st

from dashboard.data_loader import is_demo_mode


def render_documentation_page():
    st.markdown('<div class="page-title">📖 Complete Project Data, Tools & Image Provenance Documentation</div>', unsafe_allow_html=True)
    st.markdown(
        "Comprehensive architectural reference, technology inventory, data source audits, "
        "image provenance tracking, and mathematical modeling documentation for academic review and project defense."
    )

    doc_path = Path("docs/COMPLETE_PROJECT_DATA_AND_TOOLS_DOCUMENTATION.md")
    if not doc_path.is_file():
        st.error(f"Documentation file not found at `{doc_path.resolve()}`.")
        return

    content = doc_path.read_text(encoding="utf-8")

    # Mode alert badge
    if is_demo_mode():
        st.warning(
            "⚠️ **OFFLINE DEMONSTRATION MODE ACTIVE**\n\n"
            "The dashboard is currently running in offline verification mode using synthetic test fixtures. "
            "All algorithms (Random Forest, CA-Markov, Olofsson area estimation) are functioning, but displayed maps and figures are synthetic test rasters. "
            "Authentic satellite results require configuring `.env` with an active GCP project and authenticating Earth Engine (`earthengine authenticate`)."
        )
    else:
        st.success("✅ **LIVE SATELLITE MODE ACTIVE**: Verified Sentinel-2 Earth Engine connection.")

    # Action bar: Download button & Quick Navigation
    col_dl, col_nav = st.columns([2, 3])
    with col_dl:
        st.download_button(
            label="📥 Download Complete Master Documentation (Markdown)",
            data=content.encode("utf-8"),
            file_name="COMPLETE_PROJECT_DATA_AND_TOOLS_DOCUMENTATION.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col_nav:
        doc_view = st.selectbox(
            "Quick Section Focus:",
            [
                "Full Master Document (All Sections)",
                "Section 2: Tools and Technologies Used",
                "Section 3: Data Sources, Catalogs & Websites",
                "Section 4: Master Image & Map Provenance Ledger",
                "Section 5: API Keys & Cloud Configuration",
                "Section 6: Research Papers & Scientific Methodology",
                "Section 7: Historical Change Detection Methodology",
                "Section 8: Future LULC Prediction (CA-Markov)",
                "Section 9: End-to-End Traceability Chain",
                "Section 11: Step-by-Step Verification Commands",
            ],
        )

    st.markdown("---")

    # Render according to selection
    if doc_view == "Full Master Document (All Sections)":
        st.markdown(content)
    else:
        # Extract section
        sec_num = doc_view.split(":")[0].replace("Section ", "").strip()
        sec_header = f"## {sec_num}."
        
        # Split content by markdown section headers
        parts = content.split("## ")
        matching = [p for p in parts if p.startswith(f"{sec_num}.")]
        if matching:
            st.markdown(f"## {matching[0]}")
        else:
            st.markdown(content)
