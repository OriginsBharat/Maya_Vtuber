import unittest
from unittest.mock import MagicMock
from maya_ai.personas.sarjana import Sarjana

class TestDirectorSystem(unittest.TestCase):

    def setUp(self):
        """Set up mock objects for Brain and Memory."""
        self.mock_brain = MagicMock()
        self.mock_memory = MagicMock()
        self.mock_tts = MagicMock()
        self.user_id = 1

        # The brain will "process" a directive into a simple action plan
        self.mock_brain.process_directive.return_value = "Test Action Plan"
        # The persona will "execute" the plan with a simple response
        self.mock_brain.get_response.return_value = "Executing Test Action Plan in character."

    def test_01_execute_directive(self):
        """Test the full flow of a director's text directive."""
        sarjana = Sarjana(self.mock_brain, self.mock_memory, self.user_id, self.mock_tts)

        directive = "This is a test directive."
        final_response = sarjana.execute_directive(directive)

        # 1. Verify the brain was asked to process the directive
        self.mock_brain.process_directive.assert_called_once_with(
            directive, self.mock_memory.get_history.return_value
        )

        # 2. Verify the persona was asked to execute the resulting action plan
        # The persona should call the brain's get_response with a special message
        args, kwargs = self.mock_brain.get_response.call_args
        self.assertIn("My creator, originsbharat, has given me a direct order.", kwargs['latest_message'])
        self.assertIn("Test Action Plan", kwargs['latest_message'])

        # 3. Verify the final response is what we expect
        self.assertEqual(final_response, "Executing Test Action Plan in character.")

        # 4. Verify the interaction was logged correctly
        self.mock_memory.log_message.assert_any_call(self.user_id, "director", directive)
        self.mock_memory.log_message.assert_any_call(self.user_id, "assistant", final_response)

    def test_02_roleplay_response(self):
        """Test the flow of a director's voice (roleplay) message."""
        sarjana = Sarjana(self.mock_brain, self.mock_memory, self.user_id, self.mock_tts)

        roleplay_message = "A private message for you."
        sarjana.generate_response(roleplay_message, is_roleplay=True)

        # Verify the persona called get_response with the special roleplay context
        args, kwargs = self.mock_brain.get_response.call_args
        self.assertIn("private, in-character voice message", kwargs['latest_message'])
        self.assertIn(roleplay_message, kwargs['latest_message'])

if __name__ == "__main__":
    unittest.main()