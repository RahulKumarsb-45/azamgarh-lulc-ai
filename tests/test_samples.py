"""Unit tests for spatial block partitioning and inter-rater agreement."""
import numpy as np
import pandas as pd
import pytest

from src.data.sample_manager import (
    assign_points_to_blocks,
    compute_inter_rater_agreement,
    create_spatial_blocks,
    spatial_block_train_val_split,
)


def test_spatial_blocks_creation():
    bbox = (82.80, 25.70, 83.65, 26.35)
    blocks = create_spatial_blocks(bbox, block_size_km=10.0)
    assert not blocks.empty
    assert "block_id" in blocks.columns
    assert "min_lon" in blocks.columns
    assert "max_lat" in blocks.columns
    # Check that block_ids are unique
    assert len(blocks["block_id"].unique()) == len(blocks)


def test_spatial_block_zero_leakage_split():
    bbox = (82.80, 25.70, 83.65, 26.35)
    blocks = create_spatial_blocks(bbox, block_size_km=5.0)

    # Generate synthetic points
    rng = np.random.default_rng(42)
    n = 200
    df = pd.DataFrame({
        "lon": rng.uniform(bbox[0], bbox[2], n),
        "lat": rng.uniform(bbox[1], bbox[3], n),
        "class_code": rng.choice([1, 2, 3, 4, 5], n),
    })

    df_assigned = assign_points_to_blocks(df, blocks)
    train_df, val_df = spatial_block_train_val_split(df_assigned, train_ratio=0.7, random_state=42)

    train_blocks = set(train_df["block_id"])
    val_blocks = set(val_df["block_id"])

    # CRITICAL SCIENTIFIC ASSERTION: Zero spatial block overlap
    assert train_blocks.isdisjoint(val_blocks), "Spatial leakage detected! Train and val must not share blocks."
    assert len(train_df) + len(val_df) == len(df)


def test_compute_inter_rater_agreement():
    # 100% agreement
    df_perf = pd.DataFrame({
        "reviewer_1": [1, 2, 3, 4, 5],
        "reviewer_2": [1, 2, 3, 4, 5],
    })
    res_perf = compute_inter_rater_agreement(df_perf)
    assert res_perf["observed_agreement"] == 1.0
    assert res_perf["cohens_kappa"] == 1.0

    # Partial agreement
    df_part = pd.DataFrame({
        "reviewer_1": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
        "reviewer_2": [1, 1, 2, 1, 3, 3, 4, 4, 5, 2],
    })
    res_part = compute_inter_rater_agreement(df_part)
    assert res_part["observed_agreement"] == 0.8
    assert 0.0 < res_part["cohens_kappa"] < 1.0
