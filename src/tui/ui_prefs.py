import json
from pathlib import Path

PREFS_PATH = Path("config/ui_prefs.json")

DEFAULT_PREFS = {
    "autoscroll_log": True,
    "show_log_panel": True,
}


def load_prefs() -> dict:
    try:
        if PREFS_PATH.exists():
            with PREFS_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            merged = DEFAULT_PREFS.copy()
            merged.update({k: v for k, v in data.items() if k in DEFAULT_PREFS})
            return merged
    except Exception:
        pass
    return DEFAULT_PREFS.copy()


def save_prefs(prefs: dict) -> None:
    try:
        PREFS_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = DEFAULT_PREFS.copy()
        data.update({k: v for k, v in prefs.items() if k in DEFAULT_PREFS})
        with PREFS_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
