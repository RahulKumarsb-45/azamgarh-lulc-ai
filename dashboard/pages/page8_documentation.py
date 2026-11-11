"""Page 8: Project Documentation (Redirects to unified About & Data Sources)."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path for direct or multipage execution
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.pages.page_about_data_sources import render_about_page


def render_documentation_page():
    render_about_page()


if __name__ == "__main__":
    render_documentation_page()
