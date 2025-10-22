import unittest
from unittest.mock import Mock, patch
from maya_ai.personas.persona import Persona

class TestPersona(unittest.TestCase):

    def setUp(self):
        """Set up mock objects for Brain and VectorMemory."""
        self.mock_brain = Mock()
        self.mock_vector_memory = Mock()

        # Instantiate the simplified Persona
        self.persona = Persona(
            brain=self.mock_brain,
            vector_memory=self.mock_vector_memory,
            system_prompt="You are a test persona."
        )

    def test_generate_response(self):
        """Test that generate_response calls the brain with the correct parameters."""
        latest_message = "What is your name?"
        self.persona.generate_response(latest_message)

        self.mock_brain.get_response.assert_called_once()

        # Check the arguments passed to the brain's get_response
        args, kwargs = self.mock_brain.get_response.call_args
        self.assertEqual(kwargs['system_prompt'], self.persona.system_prompt)
        self.assertEqual(kwargs['latest_message'], latest_message)
        self.assertEqual(len(self.persona.conversation_history), 2) # user + assistant

    def test_summarization_is_triggered(self):
        """
        Test that conversation summarization is triggered automatically
        after the configured number of turns.
        """
        # Configure the mock Brain to return a summary
        expected_summary = "This is a test summary."
        self.mock_brain.summarize_conversation.return_value = expected_summary

        # Set a low threshold for the test
        self.persona.summary_threshold = 3
        self.persona.conversation_turn_counter = 0

        # Simulate conversation turns up to the threshold
        for i in range(self.persona.summary_threshold):
            self.mock_brain.summarize_conversation.assert_not_called()
            self.persona.generate_response(f"Test message {i}")

        # The last call should have triggered the summarization
        self.mock_brain.summarize_conversation.assert_called_once()
        self.mock_vector_memory.add_memory.assert_called_once_with(expected_summary)

        # Counter should be reset
        self.assertEqual(self.persona.conversation_turn_counter, 0)

if __name__ == '__main__':
    unittest.main()