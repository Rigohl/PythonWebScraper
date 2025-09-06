import os
from typing import Optional

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

ALIAS_MAP = {
    "ls": "Get-ChildItem",
    "ps": "Get-Process",
    "cat": "Get-Content",
    "pwd": "Get-Location",
}


def normalize_path(path: str, repo_root: Optional[str] = None) -> str:
    repo_root = repo_root or REPO_ROOT
    abs_path = os.path.abspath(os.path.join(repo_root, path))
    return abs_path


def path_exists(path: str, repo_root: Optional[str] = None) -> bool:
    abs_path = normalize_path(path, repo_root)
    return os.path.exists(abs_path)


def normalize_cmd_alias(cmd: str) -> str:
    cmd = cmd.strip().split()[0].lower()
    return ALIAS_MAP.get(cmd, cmd)


def score_confidence(matches: int, path_exists: bool, tokens: list) -> float:
    score = 0.5 if matches else 0.2
    if path_exists:
        score += 0.3
    if tokens:
        score += 0.2
    return min(score, 1.0)
