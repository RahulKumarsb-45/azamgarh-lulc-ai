"""Page: Research Paper PDF Viewer, Source Markdown & Publication Figures Gallery."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path for direct or multipage execution
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import base64
import streamlit as st


def render_research_paper_page():
    st.markdown('<div class="page-title">📄 Research Paper & Publication Figures</div>', unsafe_allow_html=True)
    st.markdown(
        "Official research paper: **'AI-Based Land Use/Land Cover Classification, Change Detection, and Future Prediction for Azamgarh District, Uttar Pradesh, India'**."
    )

    pdf_path = Path("docs/research_paper/Azamgarh_LULC_Research_Paper.pdf")
    md_path = Path("docs/research_paper/Azamgarh_LULC_Research_Paper.md")
    fig_dir = Path("docs/research_paper/figures")

    # Download action bar
    c_btn1, c_btn2, c_btn3 = st.columns([2, 2, 3])

    if pdf_path.exists():
        pdf_bytes = pdf_path.read_bytes()
        pdf_size_mb = len(pdf_bytes) / (1024 * 1024)
        with c_btn1:
            st.download_button(
                label=f"📥 Download Paper PDF ({pdf_size_mb:.2f} MB)",
                data=pdf_bytes,
                file_name="Azamgarh_LULC_Research_Paper.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    else:
        with c_btn1:
            st.error("Research paper PDF not found.")

    if md_path.exists():
        md_text = md_path.read_text(encoding="utf-8")
        with c_btn2:
            st.download_button(
                label="📝 Download Editable Markdown",
                data=md_text,
                file_name="Azamgarh_LULC_Research_Paper.md",
                mime="text/markdown",
                use_container_width=True,
            )

    with c_btn3:
        st.caption(f"Compiled Path: `{pdf_path.as_posix()}` | Status: Ready for Guide/Peer Review")

    st.markdown("---")

    # Tabs for PDF viewer, Figure Gallery, and Markdown Source
    tab_pdf, tab_gallery, tab_md = st.tabs([
        "📖 PDF Viewer",
        "🖼️ Publication Figures Gallery (300 DPI)",
        "📝 Paper Markdown Source",
    ])

    with tab_pdf:
        if pdf_path.exists():
            st.markdown("#### Research Paper PDF Document")
            base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_display = (
                f'<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=1&navpanes=1&scrollbar=1" '
                f'width="100%" height="850px" type="application/pdf" style="border: 1px solid #ddd; border-radius: 8px;"></iframe>'
            )
            st.markdown(pdf_display, unsafe_allow_html=True)
            st.caption("If your browser restricts embedded PDFs, use the download button above to open in your PDF reader.")
        else:
            st.warning("PDF file has not been built yet. Run `python docs/research_paper/build_paper_pdf.py` to compile.")

    with tab_gallery:
        st.markdown("#### High-Resolution Publication Figures (Figures 1 to 8)")
        st.markdown("All figures are compiled at 300 DPI with consistent 5-class color harmonization and verified cartographic annotations.")

        figures = [
            ("fig1_study_area.png", "Figure 1: Geographic location and administrative boundary of Azamgarh District, Uttar Pradesh, India."),
            ("fig2_satellite_spectral_composites.png", "Figure 2: Copernicus Sentinel-2 MSI multi-spectral false-color composites and cloud masking."),
            ("fig3_past_lulc_maps.png", "Figure 3: Historical LULC classification maps for Azamgarh (Past: 2019 & 2022)."),
            ("fig4_present_lulc_map.png", "Figure 4: Recent/contemporary LULC classification map for Azamgarh (Present: 2025)."),
            ("fig5_past_vs_present_change.png", "Figure 5: Past-versus-present LULC change detection (2019 vs 2025) and dynamic hotspots."),
            ("fig6_area_dynamics_chart.png", "Figure 6: Net class area trajectories and percentage change across observation periods."),
            ("fig7_future_prediction_maps.png", "Figure 7: Future LULC projections (2030 & 2035) via Cellular Automata – Markov Chain modeling."),
            ("fig8_camarkov_workflow.png", "Figure 8: Complete methodological flowchart of satellite ingestion, RF classification, and CA-Markov simulation."),
        ]

        for fname, caption in figures:
            fpath = fig_dir / fname
            if fpath.exists():
                st.markdown(f"##### {caption.split(':')[0]}")
                st.image(str(fpath), caption=caption, use_container_width=True)
                st.markdown("---")
            else:
                st.info(f"Figure `{fname}` not found in `{fig_dir}`.")

    with tab_md:
        st.markdown("#### Editable Markdown Source (`Azamgarh_LULC_Research_Paper.md`)")
        if md_path.exists():
            st.text_area("Markdown Source Code", value=md_text, height=600)
        else:
            st.warning("Markdown source file not found.")


if __name__ == "__main__":
    render_research_paper_page()
