import os
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Brain:
    """
    The core brain of Maya. It handles the fundamental interaction with the LLM.
    It is designed to be model-agnostic, so the underlying client can be swapped.
    """
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file.")

        # For now, we are using Anthropic's client. This can be replaced with any other client.
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def get_response(self, system_prompt: str, conversation_history: list, latest_message: str) -> str:
        """
        Gets a response from the language model.

        Args:
            system_prompt: The persona definition for the AI.
            conversation_history: A list of previous messages in the conversation.
            latest_message: The latest message from the user.

        Returns:
            The AI's response as a string.
        """

        # We need to construct the messages list in the format that the Anthropic API expects.
        messages = conversation_history + [{"role": "user", "content": latest_message}]

        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229", # We can change the model as needed
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
            return message.content[0].text
        except Exception as e:
            # Basic error handling
            print(f"An error occurred while communicating with the AI model: {e}")
            return "I'm sorry, I'm having trouble thinking right now."