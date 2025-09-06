import importlib.util
from pathlib import Path


def _load_module_from(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def test_sequential_processor_runs_in_order(tmp_path):
    base = Path(__file__).resolve().parents[1] / "src" / "scraper"
    sp_mod = _load_module_from(base / "sequential_processor.py", "sequential_processor")
    mc_mod = _load_module_from(base / "metrics_collector.py", "metrics_collector")

    SequentialProcessor = sp_mod.SequentialProcessor
    MetricsCollector = mc_mod.MetricsCollector

    storage = tmp_path / "brain_state.json"
    collector = MetricsCollector(storage_path=str(storage))
    processor = SequentialProcessor(collector=collector)

    urls = ["http://a.example/1", "http://b.example/2", "http://c.example/3"]
    processor.enqueue(urls)
    # run synchronously in test
    results = []
    while True:
        r = processor.run_once()
        if r is None:
            break
        results.append(r["url"])

    assert results == urls

    snap = collector.snapshot()
    assert snap["total"] == 3
    assert len(snap["last_results"]) == 3
