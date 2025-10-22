import unittest
import os
import shutil
from unittest.mock import patch, MagicMock
from maya_ai.brain.core import Brain
from maya_ai.memory.vector_memory import VectorMemory

class TestBrainIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a real VectorMemory (in-memory) and a mock OpenAI client."""
        import uuid
        self.collection_name = f"test_brain_collection_{uuid.uuid4()}"
        self.vector_memory = VectorMemory(in_memory=True, collection_name=self.collection_name)

        self.patcher = patch('maya_ai.brain.core.OpenAI')
        self.mock_openai_class = self.patcher.start()
        self.mock_client = MagicMock()
        self.mock_openai_class.return_value = self.mock_client

        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Mocked LLM response."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        self.mock_client.chat.completions.create.return_value = mock_response

        self.brain = Brain(self.vector_memory)

    def tearDown(self):
        """Clean up resources."""
        self.patcher.stop()
        self.vector_memory.client.delete_collection(name=self.collection_name)
        del self.vector_memory
        del self.brain

    def test_rag_in_get_response(self):
        """
        Test that get_response correctly retrieves a memory and augments the prompt.
        """
        # 1. Add a specific memory
        memory_text = "The user's secret password is 'bagel'."
        self.vector_memory.add_memory(memory_text)

        # 2. Call the brain's method with a relevant query
        system_prompt = "You are a helpful assistant."
        conversation_history = []
        latest_message = "What is the secret password?"

        self.brain.get_response(system_prompt, conversation_history, latest_message)

        # 3. Assert that the LLM call was made
        self.mock_client.chat.completions.create.assert_called_once()

        # 4. Inspect the arguments passed to the LLM call
        args, kwargs = self.mock_client.chat.completions.create.call_args

        # The system message should be the first in the 'messages' list
        system_message = kwargs['messages'][0]['content']

        # 5. Verify the prompt was augmented with the memory
        self.assertIn(system_prompt, system_message)
        self.assertIn("Here is some relevant context", system_message)
        self.assertIn(memory_text, system_message)

if __name__ == '__main__':
    unittest.main()