import unittest
from src.user_agent_manager import UserAgentManager
import time

class TestUserAgentManager(unittest.TestCase):

    def setUp(self):
        self.user_agents = ["Agent1", "Agent2", "Agent3"]
        # Usar una duración de bloqueo corta para que las pruebas sean rápidas
        self.manager = UserAgentManager(self.user_agents, block_duration=0.1)

    def test_get_user_agent_rotation(self):
        """Prueba que los User-Agents rotan correctamente en un ciclo."""
        agent1 = self.manager.get_user_agent()
        agent2 = self.manager.get_user_agent()
        agent3 = self.manager.get_user_agent()
        agent4 = self.manager.get_user_agent()  # Debería ser Agent1 de nuevo

        self.assertIn(agent1, self.user_agents)
        self.assertIn(agent2, self.user_agents)
        self.assertIn(agent3, self.user_agents)
        self.assertNotEqual(agent1, agent2)
        self.assertEqual(agent1, agent4, "La rotación debería volver al primer agente.")

    def test_block_and_release_user_agent(self):
        """Prueba que un User-Agent puede ser bloqueado y no se usa hasta que se libera."""
        agent_to_block = self.manager.get_user_agent()  # Agent1
        self.manager.block_user_agent(agent_to_block)

        # Los siguientes agentes no deberían ser el bloqueado
        next_agent1 = self.manager.get_user_agent()  # Agent2
        next_agent2 = self.manager.get_user_agent()  # Agent3
        self.assertNotEqual(next_agent1, agent_to_block)
        self.assertNotEqual(next_agent2, agent_to_block)

        # Liberar el agente
        self.manager.release_user_agent(agent_to_block)
        # Ahora debería estar disponible de nuevo
        next_agent3 = self.manager.get_user_agent()  # Agent1 de nuevo
        self.assertEqual(next_agent3, agent_to_block)

    def test_block_duration_expires(self):
        """Prueba que un User-Agent bloqueado se libera automáticamente después de la duración."""
        agent_to_block = self.user_agents[0]
        self.manager.block_user_agent(agent_to_block)

        # Intentar obtener todos los agentes, el bloqueado no debería aparecer
        available_agents = {self.manager.get_user_agent() for _ in range(len(self.user_agents))}
        self.assertNotIn(agent_to_block, available_agents)

        # Esperar a que el bloqueo expire
        time.sleep(0.15)

        # Ahora debería estar disponible de nuevo como el siguiente en la rotación
        next_agent = self.manager.get_user_agent()
        self.assertEqual(next_agent, agent_to_block)

if __name__ == '__main__':
    unittest.main()
