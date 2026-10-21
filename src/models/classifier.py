"""Supervised Random Forest Classifier for Land Use and Land Cover mapping.

Supports:
- Training on spectral bands and indices (NDVI, NDWI, MNDWI, NDBI).
- Hyperparameter tuning and extraction of Gini feature importances.
- Prediction with class probability outputs.
- Earth Engine SmileRandomForest translation parameter generation.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root in sys.path
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from typing import Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


DEFAULT_FEATURES = ["B2", "B3", "B4", "B8", "B11", "B12", "NDVI", "NDWI", "MNDWI", "NDBI"]


class LULCRandomForestClassifier:
    """Supervised Random Forest Classifier tailored for 5-class LULC mapping."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int | None = 16,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        random_state: int = 42,
        features: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        self.features = features or DEFAULT_FEATURES
        self.random_state = random_state
        self.rf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=-1,
            **kwargs,
        )
        self.is_fitted = False
        self.classes_: np.ndarray | None = None
        self.feature_importances_: pd.Series | None = None

    def fit(self, X: pd.DataFrame, y: pd.Series | np.ndarray) -> LULCRandomForestClassifier:
        """Fit the Random Forest classifier on training samples."""
        features_to_use = [f for f in self.features if f in X.columns]
        if not features_to_use:
            raise ValueError(f"None of the required features {self.features} found in training columns {list(X.columns)}")
        self.features = features_to_use

        X_train = X[self.features].values
        self.rf.fit(X_train, y)
        self.is_fitted = True
        self.classes_ = self.rf.classes_

        self.feature_importances_ = pd.Series(
            self.rf.feature_importances_,
            index=self.features,
        ).sort_values(ascending=False)
        return self

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict LULC class codes for input samples."""
        if not self.is_fitted:
            raise RuntimeError("Classifier must be fitted before predict() is called.")
        if isinstance(X, pd.DataFrame):
            X_mat = X[self.features].values
        else:
            X_mat = X
        return self.rf.predict(X_mat)

    def predict_proba(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict class posterior probabilities."""
        if not self.is_fitted:
            raise RuntimeError("Classifier must be fitted before predict_proba() is called.")
        if isinstance(X, pd.DataFrame):
            X_mat = X[self.features].values
        else:
            X_mat = X
        return self.rf.predict_proba(X_mat)

    def get_feature_importances(self) -> pd.DataFrame:
        """Return a formatted DataFrame of feature importances."""
        if self.feature_importances_ is None:
            raise RuntimeError("Classifier must be fitted first.")
        df = self.feature_importances_.reset_index()
        df.columns = ["feature", "importance"]
        df["importance_pct"] = (df["importance"] * 100.0).round(2)
        return df

    def to_gee_smile_rf_config(self) -> dict[str, Any]:
        """Return parameters corresponding to ee.Classifier.smileRandomForest."""
        return {
            "numberOfTrees": self.rf.n_estimators,
            "variablesPerSplit": None,  # Earth Engine default (sqrt of feature count)
            "minLeafPopulation": self.rf.min_samples_leaf,
            "seed": self.random_state,
            "inputProperties": self.features,
        }
