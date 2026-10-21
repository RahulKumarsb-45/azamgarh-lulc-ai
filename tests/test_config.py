"""Unit tests for configuration loading, schema validation, and parameter checks."""
from pathlib import Path
import re
import pytest
import yaml


def test_settings_yaml_structure():
    path = Path("config/settings.yaml")
    assert path.is_file(), "config/settings.yaml must exist."

    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert "study_area" in cfg
    assert "audit" in cfg
    assert "classification" in cfg
    assert "validation" in cfg
    assert "paths" in cfg

    sa = cfg["study_area"]
    assert sa["district"] == "Azamgarh"
    assert sa["state"] == "Uttar Pradesh"
    assert sa["target_crs"] == "EPSG:32644"
    assert sa["reference_official_area_km2"] == 4054.0

    seasons = cfg["audit"]["seasons"]
    for s in ["rabi", "zaid", "monsoon", "kharif_post"]:
        assert s in seasons
        assert "start" in seasons[s]
        assert "end" in seasons[s]


def test_class_schema_yaml_integrity():
    path = Path("config/class_schema.yaml")
    assert path.is_file(), "config/class_schema.yaml must exist."

    schema = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert "classes" in schema
    classes = schema["classes"]

    # Must contain exactly 5 standard LULC classes
    assert set(classes.keys()) == {1, 2, 3, 4, 5}

    expected_names = {
        1: "Agriculture / Cropland",
        2: "Vegetation",
        3: "Water Bodies",
        4: "Built-up Areas",
        5: "Barren / Open Land",
    }

    hex_color_re = re.compile(r"^#[0-9a-fA-F]{6}$")

    for code, info in classes.items():
        assert info["name"] == expected_names[code]
        assert "color" in info
        assert hex_color_re.match(info["color"]), f"Invalid hex color {info['color']} for class {code}"
        assert "definition" in info and len(info["definition"]) > 10


def test_dynamic_world_reference_mapping():
    schema = yaml.safe_load(Path("config/class_schema.yaml").read_text(encoding="utf-8"))
    assert "dynamic_world_reference_mapping" in schema
    dw_map = schema["dynamic_world_reference_mapping"]

    # Verify key DW classes are mapped
    assert 0 in dw_map and dw_map[0]["dw"] == "water" and dw_map[0]["to"] == 3
    assert 1 in dw_map and dw_map[1]["dw"] == "trees" and dw_map[1]["to"] == 2
    assert 4 in dw_map and dw_map[4]["dw"] == "crops" and dw_map[4]["to"] == 1
    assert 6 in dw_map and dw_map[6]["dw"] == "built" and dw_map[6]["to"] == 4
    assert 7 in dw_map and dw_map[7]["dw"] == "bare" and dw_map[7]["to"] == 5
