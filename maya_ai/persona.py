import ollama
from typing import List, Dict

class Persona:
    """
    Represents an AI persona that can interact with the user and maintain a conversation history.
    """
    def __init__(self, name: str, system_prompt: str):
        """
        Initializes a Persona instance.

        Args:
            name (str): The name of the persona.
            system_prompt (str): The initial system prompt that defines the persona's character.
        """
        self.name = name
        self.system_prompt = system_prompt
        self.history: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

    def generate_response(self, user_input: str) -> str:
        """
        Generates a response from the persona based on the user input.

        Args:
            user_input (str): The user's message or the current stimulus (e.g., a meme description).

        Returns:
            str: The persona's generated response.
        """
        self.history.append({"role": "user", "content": user_input})

        # Use a copy of the history for the API call to prevent unexpected mutations
        messages_for_api = self.history.copy()

        response = ollama.chat(
            model="llama3.1:8b-instruct-q4_0",
            messages=messages_for_api
        )

        assistant_response = response['message']['content']
        self.history.append({"role": "assistant", "content": assistant_response})

        return assistant_response

    def reset_history(self):
        """
        Resets the conversation history to just the initial system prompt.
        """
        self.history = [{"role": "system", "content": self.system_prompt}]
