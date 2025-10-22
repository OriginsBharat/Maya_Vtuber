import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
from maya_ai.main import gaming_mode
from maya_ai.brain.core import Brain

class TestGamingAgent(unittest.TestCase):

    @patch('maya_ai.main.subprocess.Popen')
    @patch('maya_ai.main.MinecraftAgent')
    @patch('maya_ai.main.time') # Mock time to prevent actual sleeping
    def test_gaming_agent_loop(self, mock_time, MockMinecraftAgent, mock_popen):
        """
        Tests the new Mineflayer-based gaming loop.
        """
        # --- Mocks Setup ---
        mock_brain = MagicMock(spec=Brain)
        mock_agent_instance = MockMinecraftAgent.return_value

        # Simulate a successful connection
        mock_agent_instance.connect.return_value = True

        # Simulate receiving world state from the bot
        mock_agent_instance.get_latest_world_state.return_value = {
            "position": {"x": 10, "y": 64, "z": 10},
            "inventory": []
        }

        # Simulate the brain's decision
        mock_brain.get_gaming_action.return_value = '{"action": "move", "direction": "forward"}'

        # --- Execution ---
        # Make the loop exit after one iteration by having the agent disconnect
        mock_agent_instance.send_command.side_effect = KeyboardInterrupt("Test complete")

        result = gaming_mode(mock_brain)

        # --- Assertions ---
        # 1. Assert that the Node.js bot was launched
        mock_popen.assert_called_once_with(["node", "mineflayer_bot/index.js"])

        # 2. Assert that the Python agent tried to connect
        mock_agent_instance.connect.assert_called_once()

        # 3. Assert that the agent was asked for the world state
        mock_agent_instance.get_latest_world_state.assert_called_once()

        # 4. Assert that the brain was asked to make a decision
        mock_brain.get_gaming_action.assert_called_once()

        # 5. Assert that the agent was commanded to perform the action
        mock_agent_instance.send_command.assert_called_once_with(
            json.loads('{"action": "move", "direction": "forward"}')
        )

        # 6. Assert that the agent was disconnected and the bot process was terminated
        mock_agent_instance.disconnect.assert_called_once()
        mock_popen.return_value.terminate.assert_called_once()

        # 7. Assert that the function returned 'exit'
        self.assertEqual(result, 'exit')

if __name__ == "__main__":
    unittest.main()