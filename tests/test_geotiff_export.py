"""Unit tests for GeoTIFF raster export, CRS georeferencing, bounding box transforms, and nodata."""
from pathlib import Path
import numpy as np
import pytest
import rasterio

from src.exports.exporter import export_geotiff


def test_export_geotiff_georeferencing(tmp_path: Path):
    arr = np.array([
        [1, 1, 2, 2],
        [1, 3, 4, 2],
        [4, 4, 5, 5],
    ], dtype=np.uint8)

    out_tif = tmp_path / "test_georef.tif"
    bbox = (82.80, 25.70, 83.65, 26.35)
    export_geotiff(arr, out_tif, bbox=bbox, crs="EPSG:4326", nodata=0)

    assert out_tif.is_file()

    with rasterio.open(out_tif) as src:
        assert src.driver == "GTiff"
        assert src.width == 4
        assert src.height == 3
        assert src.count == 1
        assert src.crs.to_string() == "EPSG:4326"
        assert src.nodata == 0

        # Check bounds
        bounds = src.bounds
        assert pytest.approx(bounds.left, 0.001) == 82.80
        assert pytest.approx(bounds.bottom, 0.001) == 25.70
        assert pytest.approx(bounds.right, 0.001) == 83.65
        assert pytest.approx(bounds.top, 0.001) == 26.35

        # Check data
        data = src.read(1)
        np.testing.assert_array_equal(data, arr)


def test_export_geotiff_utm_projection(tmp_path: Path):
    arr = np.ones((10, 10), dtype=np.int32)
    out_tif = tmp_path / "test_utm.tif"
    export_geotiff(arr, out_tif, crs="EPSG:32644")

    assert out_tif.is_file()
    with rasterio.open(out_tif) as src:
        assert src.crs.to_string() == "EPSG:32644"
        assert src.dtypes[0] == "int32"
