"""Lightweight compatibility shim for `src.intelligence.rl_agent`.

This module purposely avoids importing heavy RL libraries at import time.
Callers should import `RLAgent` via the intelligence package lazy getter
(`from src.intelligence import get_RLAgent; RLAgent = get_RLAgent()`)
or import the top-level `src.rl_agent` when they actually need the
implementation.
"""


class _RLAgentProxy:
    """Proxy for the real RLAgent implementation.

    Instantiating this proxy will attempt to import the real implementation
    from the top-level `src.rl_agent` module. If that import fails, a
    lightweight fallback object is used so tests can run in minimal
    environments.
    """

    def __init__(self, *args, **kwargs):
        # Import the real implementation lazily to avoid heavy imports at
        # package import time.
        try:
            from ..rl_agent import RLAgent as _RealRLAgent  # type: ignore

            self._impl = _RealRLAgent(*args, **kwargs)
        except Exception:
            # Minimal fallback that implements the basic expected interface.
            class _Fallback:
                def __init__(self, *a, **k):
                    pass

                def get_action(self, *a, **k):
                    return {"adjust_backoff_factor": 1.0}

                def learn(self, *a, **k):
                    return None

                def save_model(self, *a, **k):
                    return None

            self._impl = _Fallback()

    def __getattr__(self, item):
        return getattr(self._impl, item)


# Expose the proxy as the module-level name so existing imports like
# `from src.intelligence.rl_agent import RLAgent` continue to work.
RLAgent = _RLAgentProxy

__all__ = ["RLAgent"]
