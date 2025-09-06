import importlib
import inspect
import os
from typing import Any, Dict, List, Optional


class BrainPlugin:
    """Base class for brain plugins."""

    name = "base"
    version = "0.1"
    capabilities: List[str] = []

    def on_load(self, brain_ref) -> None:
        pass

    def analyze_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

    def periodic_tick(self) -> Optional[Dict[str, Any]]:
        return None


class PluginManager:
    """Dynamic plugin discovery and execution for brain extensibility."""

    def __init__(self, plugins_dir: str):
        self.plugins_dir = plugins_dir
        self.plugins: List[BrainPlugin] = []

    def discover(self):
        if not os.path.isdir(self.plugins_dir):
            return
        for fname in os.listdir(self.plugins_dir):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            mod_name = fname[:-3]
            full_module = (
                f"src.intelligence.plugins.{mod_name}"
                if self.plugins_dir.endswith("plugins")
                else mod_name
            )
            try:
                module = importlib.import_module(f"intelligence.plugins.{mod_name}")
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BrainPlugin) and obj is not BrainPlugin:
                        inst = obj()
                        self.plugins.append(inst)
            except Exception:
                continue

    def initialize(self, brain_ref):
        for p in self.plugins:
            try:
                p.on_load(brain_ref)
            except Exception:
                pass

    def process_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        outputs = []
        for p in self.plugins:
            try:
                res = p.analyze_event(event)
                if res:
                    outputs.append({"plugin": p.name, "result": res})
            except Exception:
                continue
        return outputs

    def tick(self) -> List[Dict[str, Any]]:
        outputs = []
        for p in self.plugins:
            try:
                res = p.periodic_tick()
                if res:
                    outputs.append({"plugin": p.name, "result": res})
            except Exception:
                continue
        return outputs
