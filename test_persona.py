import unittest
from unittest.mock import patch, MagicMock
from personas.persona import Persona

class TestPersona(unittest.TestCase):
    """
    Unit tests for the Persona class.
    """

    @patch('personas.persona.ollama.chat')
    def test_generate_response_updates_history(self, mock_ollama_chat):
        """
        Tests that the generate_response method correctly updates the conversation history.
        """
        # Arrange: Set up the mock response from the ollama.chat call
        mock_response = {
            'message': {
                'content': 'This is a mock response.'
            }
        }
        mock_ollama_chat.return_value = mock_response

        # Arrange: Create a Persona instance
        system_prompt = "You are a test persona."
        persona = Persona(name="Test", system_prompt=system_prompt)
        initial_history_len = len(persona.history)

        # Act: Call the method we are testing
        user_input = "Hello, world!"
        response = persona.generate_response(user_input)

        # Assert: Check that the response is what we expect
        self.assertEqual(response, "This is a mock response.")

        # Assert: Check that the history was updated correctly
        # The history should now have the system prompt, user message, and assistant response
        self.assertEqual(len(persona.history), initial_history_len + 2)
        self.assertEqual(persona.history[-2]['role'], 'user')
        self.assertEqual(persona.history[-2]['content'], user_input)
        self.assertEqual(persona.history[-1]['role'], 'assistant')
        self.assertEqual(persona.history[-1]['content'], "This is a mock response.")

        # Assert: Check that ollama.chat was called once with the correct message history
        mock_ollama_chat.assert_called_once()
        call_args = mock_ollama_chat.call_args[1]
        self.assertIn('messages', call_args)
        self.assertEqual(len(call_args['messages']), initial_history_len + 1) # History before the assistant's reply
        self.assertEqual(call_args['messages'][-1]['content'], user_input)


if __name__ == '__main__':
    unittest.main()
