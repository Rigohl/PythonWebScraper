import logging
<<<<<<< HEAD
import os
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.policies import BasePolicy
=======
import random
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
>>>>>>> 0de5c87742ffc6142484400e9bc02c49b4faaab3

logger = logging.getLogger(__name__)

class ScrapingEnv(gym.Env):
    """
<<<<<<< HEAD
    Entorno de Gymnasium personalizado para el problema de scraping.

    Espacio de Observación (Estado):
    Representa el estado de un dominio específico. Es un diccionario con métricas clave.
    - `backoff_factor`: El multiplicador de delay actual.
    - `success_rate`: Tasa de éxito (0 a 1).
    - `failure_rate`: Tasa de fallos (0 a 1).
    - `timeout_rate`: Tasa de timeouts (0 a 1).
    - `content_quality_rate`: Tasa de contenido de baja calidad (0 a 1).

    Espacio de Acción:
    Representa las decisiones que el agente puede tomar. Es un array de 3 valores continuos.
    - `backoff_factor_adjustment`: Ajuste para el backoff_factor (ej. 0.8 a 1.2).
    - `stealth_usage`: Probabilidad de usar el modo "sigiloso" (0 a 1).
    - `proxy_usage`: Probabilidad de usar un proxy (0 a 1).
    """
    metadata = {'render_modes': ['human']}

    def __init__(self, initial_metrics: dict):
        super(ScrapingEnv, self).__init__()

        # A.1.2: Definir espacios de estado y acción
        # Espacio de observación: 5 métricas continuas
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(5,), dtype=np.float32)

        # Espacio de acción: 3 acciones continuas
        # - backoff_factor: multiplicador entre 0.8 y 1.5
        # - stealth_usage: probabilidad entre 0 y 1
        # - proxy_usage: probabilidad entre 0 y 1
        self.action_space = spaces.Box(
            low=np.array([0.8, 0.0, 0.0]),
            high=np.array([1.5, 1.0, 1.0]),
            dtype=np.float32
        )

        self.current_state = self._metrics_to_state(initial_metrics)
        self.last_metrics = initial_metrics

    def _metrics_to_state(self, metrics: dict) -> np.ndarray:
        """Convierte el diccionario de métricas en un array de numpy para el estado."""
        return np.array([
            metrics.get('backoff_factor', 1.0),
            metrics.get('success_rate', 1.0),
            metrics.get('failure_rate', 0.0),
            metrics.get('timeout_rate', 0.0),
            metrics.get('content_quality_rate', 0.0)
        ], dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        """Resetea el estado del entorno."""
        super().reset(seed=seed)
        # En un escenario real, podríamos querer resetear a un estado inicial aleatorio.
        # Por ahora, lo mantenemos simple y reseteamos al último estado conocido.
        self.current_state = self._metrics_to_state(self.last_metrics)
        return self.current_state, {} # Devuelve observación e info

    def step(self, action: np.ndarray):
        """
        Ejecuta un paso en el entorno. En este diseño, el 'step' es conceptual.
        El orquestador aplicará la acción, y luego llamará a `update_state` con las nuevas métricas.
        Aquí, solo devolvemos un estado placeholder y una recompensa. La recompensa real
        se calculará en el orquestador y se usará en el método `learn` del agente.
        """
        # La acción ya ha sido aplicada por el orquestador.
        # El nuevo estado será establecido externamente a través de `update_state`.
        # La recompensa también se calcula externamente.
        reward = 0 # Placeholder
        done = False # El episodio termina cuando el orquestador lo decide
        info = {}
        return self.current_state, reward, done, False, info # obs, reward, terminated, truncated, info

    def update_state(self, new_metrics: dict):
        """Método para que el orquestador actualice el estado del entorno."""
        self.last_metrics = new_metrics
        self.current_state = self._metrics_to_state(new_metrics)

    def render(self, mode='human'):
        """Renderiza el estado actual (opcional)."""
        if mode == 'human':
            print(f"Estado Actual del Entorno: {self.current_state}")


class RLAgent:
    """
    Agente de Aprendizaje por Refuerzo que utiliza Stable-Baselines3 (PPO)
    para optimizar la estrategia de scraping por dominio.
=======
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
>>>>>>> 0de5c87742ffc6142484400e9bc02c49b4faaab3
    """
    def __init__(self, domain: str, model_path: str | None = None, training_mode: bool = True):
        self.domain = domain
        self.model_path = model_path
<<<<<<< HEAD
        self.training_mode = training_mode
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{self.domain}]")

        # Inicializar el entorno con métricas por defecto
        initial_metrics = {
            'backoff_factor': 1.0, 'success_rate': 1.0, 'failure_rate': 0.0,
            'timeout_rate': 0.0, 'content_quality_rate': 0.0
        }
        self.env = DummyVecEnv([lambda: ScrapingEnv(initial_metrics)])

        # A.1.3: Implementar un modelo PPO
        self.model = self._load_or_create_model()

    def _load_or_create_model(self) -> BasePolicy:
        """Carga un modelo PPO existente o crea uno nuevo."""
        if self.model_path and os.path.exists(self.model_path):
            self.logger.info(f"Cargando modelo PPO existente desde {self.model_path}")
            return PPO.load(self.model_path, env=self.env)
        else:
            self.logger.info("Creando un nuevo modelo PPO.")
            return PPO("MlpPolicy", self.env, verbose=0)

    def get_action(self, metrics: dict) -> dict:
        """
        Usa el modelo PPO para predecir la mejor acción basada en las métricas actuales.
        """
        self.env.envs[0].update_state(metrics)
        obs = self.env.envs[0].current_state
        
        action_array, _ = self.model.predict(obs, deterministic=not self.training_mode)

        # Decodificar la acción del array a un diccionario legible
        action_dict = {
            "backoff_factor": float(action_array[0]),
            "use_stealth": bool(action_array[1] > 0.5), # Umbral para decisión binaria
            "use_proxy": bool(action_array[2] > 0.5)
        }
        self.logger.debug(f"Métricas de entrada: {metrics}")
        self.logger.info(f"Acción predicha por PPO: {action_dict}")
        return action_dict

    def learn(self, old_metrics: dict, action: np.ndarray, reward: float, new_metrics: dict, done: bool):
        """
        Entrena el modelo PPO con la experiencia recolectada.
        """
        if not self.training_mode:
            return

        # A.1.4: Implementar la lógica de learn()
        old_state = self.env.envs[0]._metrics_to_state(old_metrics)
        new_state = self.env.envs[0]._metrics_to_state(new_metrics)

        # Stable-Baselines3 maneja el almacenamiento de la experiencia internamente.
        # El método `learn` se llama con un número total de timesteps.
        # Para un aprendizaje online, podemos hacer `learn(total_timesteps=1)`
        # después de cada `step`, pero es más eficiente recolectar un buffer
        # y entrenar periódicamente.
        # Aquí simulamos un aprendizaje paso a paso simple.
        
        # La forma correcta en SB3 es usar un ReplayBuffer o RolloutBuffer,
        # pero para una integración simple, podemos crear la tupla y
        # llamar a `train` directamente (esto es más complejo).
        
        # El enfoque más simple con SB3 es dejar que el `step` del entorno
        # maneje la recolección de datos y llamar a `learn()` periódicamente.
        # Como nuestro `step` es conceptual, simularemos el proceso.
        
        # Para este proyecto, llamaremos a `learn` con un número bajo de pasos
        # para simular el entrenamiento continuo.
        self.model.learn(total_timesteps=1)
        
        self.logger.info(f"Agente aprendió con recompensa: {reward:.2f}")

    def save_model(self):
        """A.1.5: Guarda el modelo entrenado en el disco."""
        if self.model_path:
            self.logger.info(f"Guardando modelo PPO en {self.model_path}")
            self.model.save(self.model_path)
        else:
            self.logger.warning("No se proporcionó una ruta para guardar el modelo. El progreso no se guardará.")
=======
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
>>>>>>> 0de5c87742ffc6142484400e9bc02c49b4faaab3
