"""Unit tests for Markov transition matrices, CA-Markov simulation, and historical backtesting."""
import numpy as np
import pytest

from src.models.prediction import (
    calculate_transition_matrix,
    cellular_automata_markov_simulation,
    markov_prediction,
    run_historical_backtest,
)


def test_transition_probability_row_stochastic():
    # 20x20 maps
    rng = np.random.default_rng(42)
    m1 = rng.choice([1, 2, 3, 4, 5], size=(20, 20))
    m2 = m1.copy()
    # 10% transition
    m2[rng.random((20, 20)) < 0.10] = 4

    count_df, prob_df = calculate_transition_matrix(m1, m2)
    assert not prob_df.empty

    # Each row of transition probability matrix MUST sum to 1.0 (row-stochastic property)
    row_sums = prob_df.sum(axis=1)
    for s in row_sums:
        assert pytest.approx(s, 0.001) == 1.0


def test_markov_prediction_conservation():
    init_areas = {1: 3000.0, 2: 400.0, 3: 100.0, 4: 400.0, 5: 154.0}
    total_init = sum(init_areas.values())

    # Example transition matrix with slight urban growth
    P = np.array([
        [0.95, 0.01, 0.005, 0.03, 0.005],
        [0.02, 0.94, 0.005, 0.03, 0.005],
        [0.01, 0.01, 0.97,  0.005, 0.005],
        [0.001, 0.001, 0.001, 0.995, 0.002],
        [0.05, 0.02, 0.01,  0.05, 0.87],
    ])

    pred = markov_prediction(init_areas, P, steps=1)
    total_pred = sum(pred.values())

    # Total area must be conserved across prediction steps
    assert pytest.approx(total_pred, 0.5) == total_init
    # Built-up class 4 should have grown
    assert pred[4] > init_areas[4]


def test_cellular_automata_markov_simulation():
    grid = np.ones((30, 30), dtype=np.int32)
    grid[10:20, 10:20] = 4

    P = np.eye(5)
    # Slight conversion 1 -> 4
    P[0, 0] = 0.95
    P[0, 3] = 0.05

    sim = cellular_automata_markov_simulation(grid, P, iterations=3, kernel_size=3, seed=42)
    assert sim.shape == (30, 30)
    assert set(np.unique(sim)).issubset({1, 2, 3, 4, 5})


def test_run_historical_backtest():
    rng = np.random.default_rng(42)
    m1 = rng.choice([1, 2, 3, 4, 5], size=(25, 25))
    m2 = m1.copy()
    m2[rng.random((25, 25)) < 0.05] = 4
    m3_actual = m2.copy()
    m3_actual[rng.random((25, 25)) < 0.05] = 4

    res = run_historical_backtest(m1, m2, m3_actual, years=(2019, 2022, 2025))
    assert "overall_agreement" in res
    assert "cohens_kappa" in res
    assert "figure_of_merit" in res
    assert 0.0 <= res["overall_agreement"] <= 1.0
    assert 0.0 <= res["figure_of_merit"] <= 1.0


def test_transition_probability_zero_changes():
    """Verify stability and identity matrix property when maps are completely unchanged."""
    m = np.array([
        [1, 1, 2],
        [3, 4, 5],
    ], dtype=np.int32)
    _, prob_df = calculate_transition_matrix(m, m)
    # Diagonal must be exactly 1.0
    for idx, c in enumerate([1, 2, 3, 4, 5]):
        assert pytest.approx(prob_df.iloc[idx, idx], 0.001) == 1.0

