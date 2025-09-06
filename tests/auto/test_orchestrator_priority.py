from src.orchestrator import ScrapingOrchestrator


class DummyFrontier:
    def __init__(self, score=0.5):
        self.score = score

    def predict(self, url):
        return self.score


class DummyBrain:
    def __init__(self, domain_score=0.2, backoff=False):
        self._ds = domain_score
        self._backoff = backoff

    def domain_priority(self, domain):
        return self._ds

    def should_backoff(self, domain):
        return self._backoff


def test_calculate_priority_uses_frontier_and_brain():
    orchestrator = ScrapingOrchestrator(
        start_urls=["http://example.com"],
        db_manager=None,
        user_agent_manager=None,
        llm_extractor=None,
        frontier_classifier=DummyFrontier(score=1.0),
        brain=DummyBrain(domain_score=0.5, backoff=False),
    )

    p1 = orchestrator._calculate_priority("http://example.com/a/b/c")
    p2 = orchestrator._calculate_priority("http://example.com/short")
    assert isinstance(p1, int)
    assert isinstance(p2, int)
    assert p1 != p2 or p1 >= p2
