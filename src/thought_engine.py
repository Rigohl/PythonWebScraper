from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Thought:
    content: str
    score: float


class ThoughtManager:
    def __init__(self):
        self.thoughts: List[Thought] = []

    def add_thought(self, content: str, score: float):
        self.thoughts.append(Thought(content, score))

    def select_best_thought(self) -> Optional[str]:
        if not self.thoughts:
            return None
        best = max(self.thoughts, key=lambda t: t.score)
        return best.content
