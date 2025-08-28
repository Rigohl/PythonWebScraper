import logging
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

logger = logging.getLogger(__name__)

class ScrapingEnv(gym.Env):
    """
<<<<<<< HEAD
    Entorno de Gymnasium personalizado para el problema de scraping.
    Entorno de Gymnasium para el agente de RL de scraping.
    El entorno no ejecuta el scraping real, sino que define los espacios
    de observación y acción, y recibe las recompensas y el próximo estado
    del orquestador.
    """
    def __init__(self):
        super(ScrapingEnv, self).__init__()
        # Espacio de Observación: [low_quality_ratio, failure_ratio, current_backoff]
        self.observation_space = spaces.Box(low=np.array([0.0, 0.0, 0.1]),
                                            high=np.array([1.0, 1.0, 10.0]),
                                            dtype=np.float32)
        # Espacio de Acción: 0: decrease backoff, 1: no change, 2: increase backoff
        self.action_space = spaces.Discrete(3)
        self.current_state = np.zeros(3, dtype=np.float32)

    def step(self, action):
        # Este método será llamado por el modelo PPO, pero el Orquestador es quien
        # realmente aplica la acción y determina el próximo estado y la recompensa.
        # Aquí, simplemente devolvemos un placeholder.
        # La tupla de retorno es (observation, reward, terminated, truncated, info)
        # Para nuestro uso, 'observation' y 'reward' vendrán del Orquestador.
        # 'terminated' y 'truncated' siempre serán False ya que el entorno es continuo (episodios largos).
        return self.current_state, 0.0, False, False, {}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # El estado inicial será proporcionado por el Orquestador
        self.current_state = np.zeros(3, dtype=np.float32)
        return self.current_state, {}

    def render(self):
        # No se necesita renderización visual para este entorno
        pass

    def close(self):
        pass

    def set_state(self, state_dict: dict):
        """Actualiza el estado interno del entorno con un diccionario."""
        self.current_state = np.array([
            state_dict.get("low_quality_ratio", 0.0),
            state_dict.get("failure_ratio", 0.0),
            state_dict.get("current_backoff", 0.1)
        ], dtype=np.float32)


class RLAgent:
    """
    Agente de Aprendizaje por Refuerzo (RL) que utiliza un modelo PPO.
    """
    def __init__(self, domain: str, model_path: str | None = None, training_mode: bool = True):
        self.domain = domain
        self.model_path = model_path
        self.env = ScrapingEnv()
        self.model = None
        self.vec_env = DummyVecEnv([lambda: self.env])

        if self.model_path and os.path.exists(f"{self.model_path}.zip"):
            try:
                self.model = PPO.load(self.model_path, env=self.vec_env, custom_objects={"observation_space": self.env.observation_space, "action_space": self.env.action_space})
                logger.info(f"Modelo RL cargado desde: {self.model_path}")
            except Exception as e:
                logger.error(f"Error al cargar el modelo RL desde {self.model_path}: {e}. Inicializando uno nuevo.")
                self._init_new_model()
        else:
            logger.info("No se encontró un modelo RL existente o model_path no especificado. Inicializando uno nuevo.")
            self._init_new_model()

        # Buffer para almacenar experiencias y aprender periódicamente
        self.experience_buffer = []
        self.buffer_size = 100 # Número de experiencias antes de aprender

    def _init_new_model(self):
        """Inicializa un nuevo modelo PPO."""
        self.model = PPO("MlpPolicy", self.vec_env, verbose=0, device="cpu") # Puedes cambiar device a "cuda" si tienes GPU
        logger.info("Nuevo modelo PPO inicializado.")

    def get_action(self, state_dict: dict) -> dict:
        """
        Obtiene una acción del modelo PPO basada en el estado actual.
        """
        self.env.set_state(state_dict) # Actualizar el estado del entorno
        obs = self.env.current_state

        # Stable-Baselines3 espera un batch de observaciones para predict, incluso si es solo una.
        action, _states = self.model.predict(obs, deterministic=True)
        action = action.item() # Convertir de np.array a int

        # Traducir la acción discreta a las acciones del orquestador
        if action == 0: # Decrease backoff
            return {"adjust_backoff_factor": 0.8}
        elif action == 1: # No change
            return {"adjust_backoff_factor": 1.0}
        elif action == 2: # Increase backoff
            return {"adjust_backoff_factor": 1.2}
        else:
            logger.warning(f"Acción RL desconocida: {action}. Devolviendo acción por defecto.")
            return {"adjust_backoff_factor": 1.0}

    def learn(self, state: dict, action_taken_dict: dict, reward: float, next_state: dict):
        """
        Almacena una experiencia y entrena el modelo periódicamente.
        Nota: PPO.learn() normalmente se llama con el entorno, que maneja el step interno.
        Aquí simulamos el batch para PPO, lo cual no es lo ideal para PPO, que necesita interacciones con el env.
        La forma correcta sería que el Orchestrator le dé la recompensa al env y el env.step() devuelva next_state.
        Para esta simulación, haremos un workaround.
        """
        # Convertir action_taken_dict a la acción discreta que el modelo PPO 'eligió'
        # Esto es un poco contraintuitivo, ya que action_taken_dict es lo que realmente se aplicó,
        # y necesitamos el índice de acción que lo generó.
        predicted_action_index = 1 # Por defecto, no change
        if action_taken_dict.get("adjust_backoff_factor") == 0.8: predicted_action_index = 0
        elif action_taken_dict.get("adjust_backoff_factor") == 1.2: predicted_action_index = 2

        self.experience_buffer.append((state, predicted_action_index, reward, next_state))

        if len(self.experience_buffer) >= self.buffer_size:
            logger.info("Buffer de experiencias lleno. Realizando aprendizaje PPO...")
            # En un entorno real, PPO.learn() tomaría el env y lo ejecutaría.
            # Aquí, lo llamaremos con un dummy env para que pueda procesar.
            # Esto es un placeholder; la integración completa de SB3 requiere que el entorno maneje el ciclo step().
            # Para una integración profunda, el Orchestrator necesitaría ser el 'entorno' o un Gym Wrapper.
            try:
                # Simular un entrenamiento, aunque no sea la forma ideal para PPO
                # Esto requeriría re-crear un VecEnv que pueda procesar los datos del buffer
                # O una implementación de un algoritmo off-policy como SAC/DQN.
                # Para PPO (on-policy), el learn() se hace directamente de interacciones con el env.
                # Dado que la acción y el siguiente estado son determinados por el Orchestrator,
                # esta integración es más compleja.

                # Alternativa simple: entrenar con un número fijo de pasos si el buffer se llena
                self.model.learn(total_timesteps=self.buffer_size)
                logger.info(f"Modelo PPO entrenado con {self.buffer_size} pasos.")
            except Exception as e:
                logger.error(f"Error durante el aprendizaje del modelo PPO: {e}", exc_info=True)
            finally:
                self.experience_buffer = [] # Limpiar buffer después de aprender
                self.save_model()

    def save_model(self):
        """
        Guarda el modelo PPO entrenado.
        """
        if self.model and self.model_path:
            try:
                self.model.save(self.model_path)
                logger.info(f"Modelo RL guardado en: {self.model_path}")
            except Exception as e:
                logger.error(f"Error al guardar el modelo RL en {self.model_path}: {e}")
