"""Page 5: Future Land-Cover Projections (2030 & 2035)."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path for direct or multipage execution
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.pages.page_future_predictions import render_future_predictions_page


def render_prediction_page():
    render_future_predictions_page()


if __name__ == "__main__":
    render_prediction_page()
