import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path to allow importing 'maya_ai'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from maya_ai.persona import Persona

class TestPersona(unittest.TestCase):
    """
    Unit tests for the Persona class.
    """

    def setUp(self):
        """Set up a test persona before each test."""
        self.system_prompt = "You are a test persona."
        self.persona = Persona(name="Test", system_prompt=self.system_prompt)

    @patch('maya_ai.persona.ollama.chat')
    def test_generate_response_updates_history(self, mock_ollama_chat):
        """
        Tests that the generate_response method correctly updates the conversation history.
        """
        # Arrange
        mock_response = {'message': {'content': 'This is a mock response.'}}
        mock_ollama_chat.return_value = mock_response
        initial_history_len = len(self.persona.history)
        user_input = "Hello, world!"

        # Act
        response = self.persona.generate_response(user_input)

        # Assert
        self.assertEqual(response, "This is a mock response.")
        self.assertEqual(len(self.persona.history), initial_history_len + 2) # User + Assistant
        self.assertEqual(self.persona.history[-2]['role'], 'user')
        self.assertEqual(self.persona.history[-2]['content'], user_input)
        self.assertEqual(self.persona.history[-1]['role'], 'assistant')
        self.assertEqual(self.persona.history[-1]['content'], "This is a mock response.")

    @patch('maya_ai.persona.ollama.chat')
    def test_api_call_uses_history_copy(self, mock_ollama_chat):
        """
        Tests that the ollama.chat method is called with a copy of the history,
        not a reference to the instance's history list.
        """
        # Arrange
        mock_response = {'message': {'content': 'Another mock response.'}}
        mock_ollama_chat.return_value = mock_response

        # Act
        self.persona.generate_response("Test input")

        # Assert
        mock_ollama_chat.assert_called_once()
        call_args = mock_ollama_chat.call_args[1]
        messages_sent_to_api = call_args['messages']

        # The list sent to the API should have 2 items (system, user)
        self.assertEqual(len(messages_sent_to_api), 2)
        # The instance's history should have 3 (system, user, assistant)
        self.assertEqual(len(self.persona.history), 3)

    def test_reset_history(self):
        """
        Tests that the reset_history method correctly resets the conversation history.
        """
        # Arrange
        self.persona.history.append({"role": "user", "content": "test"})
        self.persona.history.append({"role": "assistant", "content": "test response"})
        self.assertNotEqual(len(self.persona.history), 1)

        # Act
        self.persona.reset_history()

        # Assert
        self.assertEqual(len(self.persona.history), 1)
        self.assertEqual(self.persona.history[0]['role'], 'system')
        self.assertEqual(self.persona.history[0]['content'], self.system_prompt)

if __name__ == '__main__':
    unittest.main()
