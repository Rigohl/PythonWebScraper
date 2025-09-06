"""
Reinforcement learning wrapper for adaptive scraping.

This module defines an RL environment and agent for controlling the
backoff factor of a web scraper.  It attempts to load the PPO algorithm
from stable_baselines3 when available; if the dependency is missing, it
falls back to a dummy model that simply returns no‑change actions.  This
design keeps the orchestrator functional in offline test environments.
"""

from __future__ import annotations

import logging
import os
from typing import Optional, Tuple

import numpy as np

try:
    import gymnasium as gym  # type: ignore
    from gymnasium import spaces  # type: ignore
    from stable_baselines3 import PPO  # type: ignore
    from stable_baselines3.common.vec_env import DummyVecEnv  # type: ignore

    RL_AVAILABLE = True
    Env = gym.Env
except Exception:
    # Provide minimal shims when RL libraries are missing
    RL_AVAILABLE = False
    Env = object

    # Minimal space shims used for tests when `gymnasium` is not installed.
    class _BoxShim:
        def __init__(self, shape):
            self.shape = tuple(shape)

    class _DiscreteShim:
        def __init__(self, n):
            self.n = int(n)


logger = logging.getLogger(__name__)


class ScrapingEnv(Env):
    """Gymnasium environment for the RL agent.

    The environment defines a continuous observation space representing
    domain metrics and a discrete action space with three possible actions:
    decrease, keep or increase the backoff factor.  When gymnasium is not
    installed, this class provides the minimal interface expected by the
    agent.
    """

    def __init__(self) -> None:
        super().__init__()
        # Define observation and action spaces using gymnasium types when
        # available, otherwise use lightweight shims that provide the
        # attributes tests need (`shape` and `n`). This keeps the class
        # usable in environments without gymnasium installed.
        if RL_AVAILABLE:
            self.observation_space = spaces.Box(
                low=np.array([0.0, 0.0, 0.1]),
                high=np.array([1.0, 1.0, 10.0]),
                dtype=np.float32,
            )
            self.action_space = spaces.Discrete(3)
        else:
            self.observation_space = _BoxShim((3,))
            self.action_space = _DiscreteShim(3)
        self.current_state = np.zeros(3, dtype=np.float32)

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, dict]:
        # Placeholder; the orchestrator drives the environment.
        return self.current_state, 0.0, False, False, {}

    def reset(self, seed: Optional[int] = None) -> Tuple[np.ndarray, dict]:
        self.current_state = np.zeros(3, dtype=np.float32)
        return self.current_state, {}

    def render(self, mode: str = "human") -> None:
        """Render the environment. Required by gymnasium interface."""

    def close(self) -> None:
        """Optional cleanup hook. Mirrors gymnasium Env.close()."""
        # No-op for the simple test environment; present for API parity.
        return None

    def set_state(self, state_dict: dict) -> None:
        """Update the internal state representation from a metrics dictionary."""
        self.current_state = np.array(
            [
                state_dict.get("low_quality_ratio", 0.0),
                state_dict.get("failure_ratio", 0.0),
                state_dict.get("current_backoff", 0.1),
            ],
            dtype=np.float32,
        )


class DummyModel:
    """Simple fallback model used when RL libraries are unavailable.

    The dummy model always returns the "no change" action and performs no
    learning.  It exposes the same ``predict``, ``learn`` and ``save``
    interface expected by :class:`RLAgent`.
    """

    def __init__(self) -> None:
        pass

    def predict(
        self, obs: np.ndarray, deterministic: bool = True
    ) -> Tuple[np.ndarray, None]:
        return np.array([1]), None  # action 1 corresponds to no change

    def learn(self, total_timesteps: int) -> None:
        # No learning performed
        pass

    def save(self, path: str) -> None:
        # Saving does nothing in dummy mode
        pass


class RLAgent:
    """Reinforcement Learning agent controlling the scraper backoff factor.

    The agent uses a PPO model from stable_baselines3 when available; if
    dependencies are missing it falls back to a dummy model that issues
    neutral actions and does not learn.  The ``domain`` parameter is used
    solely to namespace the model on disk.  The ``model_path`` is an
    optional filesystem path for loading and saving the trained model.
    """

    def __init__(
        self,
        domain: Optional[str] = None,
        model_path: Optional[str] = None,
        training_mode: bool = True,
    ) -> None:
        self.domain = domain
        self.model_path = model_path
        self.training_mode = training_mode
        self.env = ScrapingEnv()
        self.experience_buffer: list[tuple] = []
        self.buffer_size = 100

        if RL_AVAILABLE:
            self.vec_env = DummyVecEnv([lambda: self.env])  # type: ignore
            # Load existing model if possible
            if model_path and os.path.exists(f"{model_path}.zip"):
                try:
                    self.model = PPO.load(model_path, env=self.vec_env)  # type: ignore
                    logger.info(f"Modelo RL cargado desde: {model_path}")
                except Exception as e:
                    logger.error(
                        "Error al cargar el modelo RL desde %s: %s. Creando uno nuevo.",
                        model_path,
                        e,
                    )
                    self.model = PPO(
                        "MlpPolicy", self.vec_env, verbose=0, device="cpu"
                    )  # type: ignore
            else:
                self.model = PPO("MlpPolicy", self.vec_env, verbose=0, device="cpu")  # type: ignore
                logger.info("Nuevo modelo PPO inicializado.")
        else:
            # Fallback: dummy model
            self.model = DummyModel()
            logger.warning(
                "stable_baselines3 no está disponible; usando DummyModel para RL."
            )

    def get_action(self, state_dict: dict) -> dict:
        """Compute an action dictionary from a state dictionary."""
        self.env.set_state(state_dict)
        obs = self.env.current_state
        action, _ = self.model.predict(obs, deterministic=True)

        # Handle NumPy array conversion safely to avoid deprecation warnings
        if isinstance(action, np.ndarray):
            if action.ndim == 0:  # scalar array
                action_val = int(action.item())
            else:  # multi-dimensional array
                action_val = int(action[0])
        elif isinstance(action, (list, tuple)):
            action_val = int(action[0]) if action else 1  # default to no change
        else:
            action_val = int(action)

        if action_val == 0:
            return {"adjust_backoff_factor": 0.8}
        if action_val == 1:
            return {"adjust_backoff_factor": 1.0}
        if action_val == 2:
            return {"adjust_backoff_factor": 1.2}
        logger.warning(
            f"Acción RL desconocida: {action_val}. Devolviendo acción por defecto."
        )
        return {"adjust_backoff_factor": 1.0}

    def learn(
        self, state: dict, action_taken: dict, reward: float, next_state: dict
    ) -> None:
        """Append an experience to the buffer and train when full.

        In dummy mode this method records the experience but does not
        actually invoke learning.  With PPO available it performs a
        rudimentary training step when the experience buffer reaches
        ``buffer_size``.  Note that this is a simplification; full on‑policy
        training would require direct interaction with the environment.
        """
        # Map the action dict back to an index
        if action_taken.get("adjust_backoff_factor") == 0.8:
            act_idx = 0
        elif action_taken.get("adjust_backoff_factor") == 1.2:
            act_idx = 2
        else:
            act_idx = 1
        self.experience_buffer.append((state, act_idx, reward, next_state))
        # When RL is unavailable, do nothing more
        if not RL_AVAILABLE:
            return
        # Trigger training if buffer is full
        if len(self.experience_buffer) >= self.buffer_size:
            try:
                self.model.learn(total_timesteps=self.buffer_size)
                logger.info(f"Modelo PPO entrenado con {self.buffer_size} pasos.")
            except Exception as e:
                logger.error(
                    f"Error durante el aprendizaje del modelo PPO: {e}", exc_info=True
                )
            finally:
                self.experience_buffer = []
                self.save_model()

    def save_model(self) -> None:
        """Persist the trained model to disk if a path was provided."""
        if RL_AVAILABLE and self.model_path:
            try:
                self.model.save(self.model_path)
                logger.info(f"Modelo RL guardado en: {self.model_path}")
            except Exception as e:
                logger.error(f"Error al guardar el modelo RL en {self.model_path}: {e}")
