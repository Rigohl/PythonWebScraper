"""
Heuristic frontier classifier for URL prioritisation.

This module provides a lightweight ``FrontierClassifier`` that extracts
rudimentary features from a URL – path depth, query parameter count and a
binary indicator for HTTPS – and computes a simple score.  The score can
then be used by a crawling orchestrator to prioritise which links to
process first.  A more sophisticated implementation could load a
pre‑trained machine learning model; here we maintain a deterministic
heuristic for ease of testing.
"""

from __future__ import annotations

import logging
from typing import Tuple
from urllib.parse import urlparse

import numpy as np


class FrontierClassifier:
    """Dummy classifier for estimating the promise of a URL.

    The classifier exposes two methods:

    * :meth:`extract_features` converts a URL into a numeric feature vector.
    * :meth:`predict_score` computes a floating‑point score from the features
      using a simple heuristic: deeper paths and HTTPS receive higher
      scores.
    """

    def __init__(self, model_path: str | None = None) -> None:
        # ``model_path`` is accepted for forward compatibility but unused.
        self.model_path = model_path

    @staticmethod
    def extract_features(url: str) -> np.ndarray:
        """Return a feature vector ``[path_depth, query_params, is_https]``.

        Args:
            url: The URL to extract features from.

        Returns:
            A 1×3 numpy array of integers.
        """
        parsed = urlparse(url)
        path_segments = [segment for segment in parsed.path.split("/") if segment]
        query_params = parsed.query.split("&") if parsed.query else []
        features = [
            len(path_segments),
            len(query_params),
            1 if parsed.scheme == "https" else 0,
        ]
        return np.array(features, dtype=float).reshape(1, -1)

    def predict_score(self, url: str) -> float:
        """Compute a heuristic score for the given URL.

        The score is computed as ``0.1 * path_depth + 0.5 * is_https``.

        Args:
            url: The URL to score.

        Returns:
            float: The heuristic promise score; larger values indicate higher priority.
        """
        features = self.extract_features(url)
        path_depth = features[0, 0]
        is_https = features[0, 2]
        return float(path_depth * 0.1 + is_https * 0.5)

    # Maintain backwards compatibility with older callers using ``predict``
    def predict(self, url: str) -> float:
        """Alias for :meth:`predict_score`.  Provided for backwards compatibility."""
        return self.predict_score(url)

    def train(self, dataset_path: str) -> None:
        """Placeholder train method.

        This method accepts a path to a dataset but does nothing.  It exists
        solely to mirror the interface of a real classifier.  In a real
        implementation, you would load the dataset, extract features and
        train a model, persisting it to ``self.model_path`` for later use.
        """
        # This is a placeholder. In a real implementation, you would train a model.
        logging.info(f"Dummy training of classifier with dataset: {dataset_path}")
