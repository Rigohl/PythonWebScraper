"""Unit tests for the refactored FrontierClassifier."""

import unittest
import numpy as np

from src.frontier_classifier import FrontierClassifier


class TestFrontierClassifier(unittest.TestCase):
    def setUp(self) -> None:
        self.classifier = FrontierClassifier()

    def test_extract_features(self):
        url = "https://example.com/path/to/page?param=1&b=2"
        features = self.classifier.extract_features(url)
        self.assertIsInstance(features, np.ndarray)
        self.assertEqual(features.shape, (1, 3))
        # path depth = 2, query params = 2, https flag = 1
        self.assertTrue(np.array_equal(features[0], np.array([2.0, 2.0, 1.0])))

    def test_predict_score(self):
        http_score = self.classifier.predict_score("http://example.com/a")
        https_score = self.classifier.predict_score("https://example.com/a")
        self.assertAlmostEqual(https_score - http_score, 0.5)
        deeper = self.classifier.predict_score("http://example.com/one/two/three")
        shallow = self.classifier.predict_score("http://example.com/")
        self.assertGreater(deeper, shallow)

    def test_predict_alias(self):
        score1 = self.classifier.predict("http://example.com")
        score2 = self.classifier.predict_score("http://example.com")
        self.assertEqual(score1, score2)


if __name__ == "__main__":
    unittest.main()