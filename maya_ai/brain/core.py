import ollama
from loguru import logger
from maya_ai.config.config_loader import get_config
import time

class Brain:
    """
    The core brain of Maya, responsible for communicating with the Ollama LLM.
    """
    def __init__(self):
        """
        Initializes the Brain with a specific LLM model from the config.
        """
        self.config = get_config()
        self.model = self.config.brain_model

    def get_response(self, system_prompt: str, conversation_history: list[dict]) -> str:
        """
        Gets a response from the LLM with retry logic.
        """
        messages = [{"role": "system", "content": system_prompt}] + conversation_history

        for attempt in range(3):
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=messages,
                    options={'temperature': self.config.get('brain', 'temperature', 0.8)}
                )
                return response['message']['content']
            except Exception as e:
                logger.error(f"Error communicating with Ollama (attempt {attempt + 1}/3): {e}", exc_info=True)
                if attempt < 2:
                    time.sleep(5)
        return "I am having trouble thinking right now."

    def get_gaming_action(self, world_state: dict, goal: str) -> str:
        """
        Gets the next gaming action from the LLM.
        """
        system_prompt = f"""
You are an AI playing Minecraft. Your goal is to: {goal}.
Based on the current world state, decide the next action to take.
The world state is: {world_state}.
Your response must be a JSON object with two keys: "command" and "args".
The "command" must be a valid mineflayer bot command (e.g., "chat", "equip", "toss", "move").
The "args" must be a list of arguments for the command.
Example: {{"command": "chat", "args": ["Hello, world!"]}}
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
            logger.error(f"Error getting gaming action from Ollama: {e}", exc_info=True)
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
            logger.error(f"Error choosing skill from Ollama: {e}", exc_info=True)
            return "{}"

    def see_and_think(self, prompt: str, image_path: str) -> str:
        """
        Analyzes an image with a text prompt using a multimodal model (LLaVA).
        """
        logger.info(f"Analyzing image {image_path} with prompt: '{prompt}'")
        try:
            # The llava model is hardcoded for now, as it's our primary visual model.
            # This could be made configurable in the future if needed.
            response = ollama.chat(
                model='llava',
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [image_path]
                    }
                ]
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error during multimodal analysis with Ollama: {e}", exc_info=True)
            return "I am having trouble understanding what I'm seeing right now."
