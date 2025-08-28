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

    def test_acquire_user_agent(self):
        ua = self.manager.acquire_user_agent()
        self.assertIn(ua, self.test_user_agents)
        self.assertIn(ua, self.manager.in_use_user_agents)
        self.assertNotIn(ua, self.manager.available_user_agents)

    def test_acquire_all_user_agents(self):
        acquired_uas = []
        for _ in range(len(self.test_user_agents)):
            ua = self.manager.acquire_user_agent()
            acquired_uas.append(ua)
        
        self.assertEqual(len(self.manager.available_user_agents), 0)
        self.assertEqual(len(self.manager.in_use_user_agents), len(self.test_user_agents))
        self.assertIsNone(self.manager.acquire_user_agent()) # Should return None if no UAs available

    def test_release_user_agent(self):
        ua = self.manager.acquire_user_agent()
        self.manager.release_user_agent(ua)
        self.assertIn(ua, self.manager.available_user_agents)
        self.assertNotIn(ua, self.manager.in_use_user_agents)

    def test_block_user_agent(self):
        ua = self.manager.acquire_user_agent()
        self.manager.block_user_agent(ua, block_time=1)
        self.assertNotIn(ua, self.manager.available_user_agents)
        self.assertNotIn(ua, self.manager.in_use_user_agents)
        self.assertIn(ua, self.manager.blocked_user_agents)
        
        # Try to acquire a blocked UA immediately
        self.assertIsNone(self.manager.acquire_user_agent())

    def test_unblock_user_agents_after_time(self):
        ua = self.manager.acquire_user_agent()
        self.manager.block_user_agent(ua, block_time=1) # Block for 1 second
        
        # Simulate time passing
        time.sleep(1.1)
        
        # Now, the UA should be available again
        unblocked_ua = self.manager.acquire_user_agent()
        self.assertEqual(unblocked_ua, ua)
        self.assertNotIn(ua, self.manager.blocked_user_agents)

    def test_acquire_prefers_unblocked(self):
        ua1 = self.manager.acquire_user_agent() # UA_1
        self.manager.block_user_agent(ua1, block_time=10)
        
        ua2 = self.manager.acquire_user_agent() # UA_2
        self.assertNotEqual(ua1, ua2)
        self.assertIn(ua1, self.manager.blocked_user_agents)
        self.assertIn(ua2, self.manager.in_use_user_agents)

        self.manager.release_user_agent(ua2)
        self.assertIn(ua2, self.manager.available_user_agents)

        # UA1 is still blocked, so UA2 should be acquired again
        ua_reacquired = self.manager.acquire_user_agent()
        self.assertEqual(ua_reacquired, ua2)

    def test_no_user_agents_initially(self):
        manager = UserAgentManager([])
        self.assertIsNone(manager.acquire_user_agent())

    def test_release_non_existent_user_agent(self):
        # Should not raise an error, just do nothing
        self.manager.release_user_agent("NON_EXISTENT_UA")
        # No assertions needed, just ensuring it doesn't crash

    def test_block_non_existent_user_agent(self):
        # Should not raise an error, just do nothing
        self.manager.block_user_agent("NON_EXISTENT_UA", block_time=1)
        # No assertions needed, just ensuring it doesn't crash

if __name__ == '__main__':
    unittest.main()
