import pytest
import numpy as np
from src.frontier_classifier import FrontierClassifier

@pytest.fixture
def frontier_classifier():
    return FrontierClassifier()

def test_frontier_classifier_init(frontier_classifier):
    assert isinstance(frontier_classifier, FrontierClassifier)

@pytest.mark.parametrize(
    "url, expected_features",
    [
        ("http://example.com/path/to/page?param=1", [3, 1, 0]),
        ("https://example.com/", [0, 0, 1]),
        ("http://example.com/one/two/three", [3, 0, 0]),
        ("https://example.com/page?a=1&b=2", [1, 2, 1]),
        ("http://example.com/path/", [1, 0, 0]),
    ],
)
def test_extract_features(frontier_classifier, url, expected_features):
    features = frontier_classifier._extract_features(url)
    assert isinstance(features, np.ndarray)
    assert features.shape == (1, 3)
    assert np.array_equal(features[0], np.array(expected_features))

def test_predict_returns_float(frontier_classifier):
    score = frontier_classifier.predict("http://example.com")
    assert isinstance(score, float)

def test_predict_dummy_logic(frontier_classifier):
    # Deeper path should have higher score (path_depth * 0.1)
    score1 = frontier_classifier.predict("http://example.com/page1") # path_depth = 1
    score2 = frontier_classifier.predict("http://example.com/path/to/page2") # path_depth = 3
    assert score2 > score1

    # HTTPS should add 0.5 to score
    score_http = frontier_classifier.predict("http://example.com/simple")
    score_https = frontier_classifier.predict("https://example.com/simple")
    assert score_https == score_http + 0.5

def test_train_dummy_method(frontier_classifier):
    # Should not raise any errors
    try:
        frontier_classifier.train("dummy_dataset.csv")
    except Exception as e:
        pytest.fail(f"train method raised an unexpected exception: {e}")
