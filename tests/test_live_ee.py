"""Live Earth Engine test suite (requires active network access and valid credentials)."""
import os
import pytest
from src.data.gee_init import check_env_file, is_authenticated


@pytest.mark.live_ee
def test_live_earth_engine_connectivity():
    has_creds = is_authenticated()
    env_exists, _ = check_env_file()
    project = os.environ.get("EE_PROJECT")

    if not (has_creds and env_exists and project and project not in ("your-gcp-project-id", "YOUR_GCP_PROJECT_ID")):
        pytest.skip("Skipping live GEE test: credentials or EE_PROJECT not configured locally.")

    import ee
    from src.data.gee_init import init_ee
    proj = init_ee(raise_exit=False)
    assert proj is not None

    # Test querying FAO GAUL boundary for Azamgarh
    fc = ee.FeatureCollection("FAO/GAUL/2015/level2")
    hit = fc.filter(ee.Filter.eq("ADM1_NAME", "Uttar Pradesh")).filter(ee.Filter.eq("ADM2_NAME", "Azamgarh"))
    n = hit.size().getInfo()
    assert n == 1, f"Expected 1 feature for Azamgarh District, got {n}"
