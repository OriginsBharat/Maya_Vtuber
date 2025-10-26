import ollama

class Brain:
    """
    The core brain of Maya, responsible for communicating with the Ollama LLM.
    """
    def __init__(self, model="Meta-Llama-3.1-8B-Instruct"):
        """
        Initializes the Brain with a specific LLM model.
        """
        self.model = model

    def get_response(self, system_prompt: str, conversation_history: list) -> str:
        """
        Gets a response from the LLM based on the system prompt and conversation history.

        Args:
            system_prompt: The initial instruction for the persona.
            conversation_history: The list of previous messages in the conversation.

        Returns:
            The response from the LLM as a string.
        """
        messages = [
            {"role": "system", "content": system_prompt}
        ] + conversation_history

        try:
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            return "I am having trouble thinking right now."
