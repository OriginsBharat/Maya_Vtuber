import unittest
from unittest.mock import MagicMock
from maya_ai.personas.sarjana import Sarjana
from maya_ai.personas.durjana import Durjana

class TestPersonas(unittest.TestCase):

    def setUp(self):
        """Set up mock objects for Brain and Memory."""
        # Mock the Brain class to simulate its behavior without making real API calls
        self.mock_brain = MagicMock()

        # Mock the MemoryDatabase class
        self.mock_memory = MagicMock()
        self.mock_tts = MagicMock()

        self.user_id = 1

        # Pre-canned response from the "brain"
        self.mock_brain.get_response.return_value = "This is a test response from the mock brain."
        # Pre-canned history from "memory"
        self.mock_memory.get_history.return_value = [{"role": "user", "content": "Initial message"}]

    def test_01_sarjana_persona(self):
        """Test if Sarjana uses the correct system prompt."""
        sarjana = Sarjana(self.mock_brain, self.mock_memory, self.user_id, self.mock_tts)

        # Generate a response
        latest_message = "Hello Sarjana"
        response = sarjana.generate_response(latest_message)

        # Verify that the brain's get_response method was called correctly
        self.mock_brain.get_response.assert_called_once()

        # Get the arguments passed to get_response
        args, kwargs = self.mock_brain.get_response.call_args

        # Check if the system_prompt contains key phrases for Sarjana
        system_prompt = kwargs['system_prompt']
        self.assertIn("You are Sarjana", system_prompt)
        self.assertIn("the 'good' daughter", system_prompt)
        self.assertIn("You must speak exclusively in Hinglish", system_prompt)

        # Check that the memory was updated
        self.mock_memory.log_message.assert_any_call(self.user_id, "user", latest_message)
        self.mock_memory.log_message.assert_any_call(self.user_id, "assistant", self.mock_brain.get_response.return_value)

    def test_02_durjana_persona(self):
        """Test if Durjana uses the correct system prompt."""
        durjana = Durjana(self.mock_brain, self.mock_memory, self.user_id, self.mock_tts)

        # Generate a response
        latest_message = "Hello Durjana"
        response = durjana.generate_response(latest_message)

        # Verify that the brain's get_response method was called correctly
        self.mock_brain.get_response.assert_called_once()

        # Get the arguments passed to get_response
        args, kwargs = self.mock_brain.get_response.call_args

        # Check if the system_prompt contains key phrases for Durjana
        system_prompt = kwargs['system_prompt']
        self.assertIn("You are Durjana", system_prompt)
        self.assertIn("the 'bratty' daughter", system_prompt)
        self.assertIn("tsundere attitude", system_prompt)

        # Check that the memory was updated
        self.mock_memory.log_message.assert_any_call(self.user_id, "user", latest_message)
        self.mock_memory.log_message.assert_any_call(self.user_id, "assistant", self.mock_brain.get_response.return_value)

if __name__ == "__main__":
    unittest.main()