import ollama

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
        self.history = [{"role": "system", "content": system_prompt}]

    def generate_response(self, user_input: str) -> str:
        """
        Generates a response from the persona based on the user input.

        Args:
            user_input (str): The user's message or the current stimulus (e.g., a meme description).

        Returns:
            str: The persona's generated response.
        """
        self.history.append({"role": "user", "content": user_input})

        response = ollama.chat(
            model="llama3.1:8b-instruct-q4_0",
            messages=self.history.copy()
        )

        assistant_response = response['message']['content']
        self.history.append({"role": "assistant", "content": assistant_response})

        return assistant_response
