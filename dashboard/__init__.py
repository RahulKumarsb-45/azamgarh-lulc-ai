"""Azamgarh LULC Monitoring & Research System - Dashboard Package."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
