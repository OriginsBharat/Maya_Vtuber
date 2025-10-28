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

    def parse_directive(self, directive: str) -> tuple:
        """
        Parses a complex directive into a command and arguments.
        """
        parts = directive.split()
        command = parts[0]
        args = parts[1:]
        return command, args

    def get_gaming_action(self, world_state: dict, goal: str) -> str:
        """
        Gets the next gaming action from the LLM based on the world state and goal.
        """
        system_prompt = f"""
You are an AI playing Minecraft. Your goal is to: {goal}.
Based on the current world state, decide the next action to take.
The world state is: {world_state}.
Respond with a JSON object representing the action.
Example: {{"command": "move", "args": {{"x": 10, "y": 64, "z": -5}}}}
"""
        messages = [{"role": "system", "content": system_prompt}]
        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                format="json"
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            return "{}"

    def choose_skill(self, directive: str, skills: list) -> str:
        """
        Chooses the best skill to use to respond to a directive.
        """
        system_prompt = f"""
You are an AI assistant that chooses the best skill to respond to a user's directive.
The available skills are:
{skills}

The user's directive is: "{directive}"

Respond with a JSON object containing the chosen skill, action, and arguments.
If you are unsure, respond with {{"skill": "ask_creator", "action": "ask", "args": {{"question": "Your question here"}}}}
Example: {{"skill": "Reddit Scraper Skill", "action": "get_top_posts", "args": {{"subreddit_name": "memes", "limit": 5}}}}
"""
        messages = [{"role": "system", "content": system_prompt}]
        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                format="json"
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            return "{}"
