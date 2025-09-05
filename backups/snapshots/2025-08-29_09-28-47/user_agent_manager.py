import random
import time
from datetime import datetime, timedelta

class UserAgentManager:
    """
    Gestiona un pool de User-Agents, permitiendo rotación y bloqueo temporal.
    """
    def __init__(self, user_agents: list[str]):
        if not user_agents:
            raise ValueError("La lista de User-Agents no puede estar vacía.")
        self.user_agents = user_agents
        self.available_user_agents = set(user_agents)
        self.blocked_user_agents = {} # {ua: block_until_timestamp}
        self.current_ua_index = 0

    def _clean_blocked_user_agents(self):
        """Libera User-Agents bloqueados cuya duración ha expirado."""
        now = datetime.now()
        for ua, block_until in list(self.blocked_user_agents.items()):
            if now > block_until:
                self.available_user_agents.add(ua)
                del self.blocked_user_agents[ua]

    def get_user_agent(self) -> str:
        """
        Retorna un User-Agent disponible. Si todos están bloqueados, retorna uno aleatorio
        de la lista original (podría estar bloqueado, pero es la única opción).
        """
        self._clean_blocked_user_agents()
        
        if not self.available_user_agents:
            # Si todos están bloqueados, rotar entre la lista original
            self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
            return self.user_agents[self.current_ua_index]
        
        # Rotación simple entre los disponibles
        ua_list = list(self.available_user_agents)
        self.current_ua_index = (self.current_ua_index + 1) % len(ua_list)
        return ua_list[self.current_ua_index]

    def block_user_agent(self, user_agent: str, duration_seconds: int = 300):
        """
        Bloquea un User-Agent por una duración específica.
        """
        if user_agent in self.available_user_agents:
            self.available_user_agents.remove(user_agent)
        self.blocked_user_agents[user_agent] = datetime.now() + timedelta(seconds=duration_seconds)
        
    def release_user_agent(self, user_agent: str):
        """
        Libera un User-Agent bloqueado antes de tiempo.
        """
        if user_agent in self.blocked_user_agents:
            del self.blocked_user_agents[user_agent]
            self.available_user_agents.add(user_agent)
