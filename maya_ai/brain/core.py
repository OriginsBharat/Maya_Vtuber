import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Brain:
    """
    The core brain of Maya. It connects to a local LLM server (Ollama)
    to handle all reasoning and language generation tasks.
    """
    def __init__(self):
        self.model_name = os.getenv("OLLAMA_MODEL")
        if not self.model_name:
            raise ValueError("OLLAMA_MODEL not found in .env file. Please specify the model to use.")

        # Point the client to the local Ollama server
        self.client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='ollama', # required, but unused
        )
        print(f"🧠 Brain initialized to use local LLM: {self.model_name}")

    def get_response(self, system_prompt: str, conversation_history: list, latest_message: str) -> str:
        """
        Gets a standard conversational response from the language model.
        """
        messages = conversation_history + [{"role": "user", "content": latest_message}]
        return self._execute_llm_call(system_prompt, messages)

    def process_directive(self, directive: str, conversation_history: list) -> str:
        """
        Processes a high-level directive from the director into an action plan.
        """
        print(f"🧠 Brain processing directive: '{directive}'")
        directive_system_prompt = """\
You are a logical processor for an AI VTuber. Your job is to translate a high-level directive from the director into a clear, actionable instruction for the AI persona.
The directive will be a natural language command. You must analyze it and the recent chat history to determine the best course of action.
Your output MUST be one of two things:
1. A short, clear, in-character instruction for a simple action.
2. A multi-step plan in the format `[PLAN: step1, step2, step3]` for complex actions like video creation.

Example Directive: "make fun of a creepy chatter"
Your Action Plan Output: "Find the comment from 'CreepyUser' and roast them for being weird."

Example Directive: "create a video about dogs from r/aww"
Your Action Plan Output: "[PLAN: scrape_content r/aww dogs, generate_commentary, synthesize_audio, create_video]"
"""
        directive_message = f"""\
Directive: "{directive}"
Recent Chat History:
{self._format_history_for_prompt(conversation_history)}

Your Action Plan Output:"""
        messages = [{"role": "user", "content": directive_message}]
        action_plan = self._execute_llm_call(directive_system_prompt, messages)
        print(f"💡 Brain generated action plan: '{action_plan}'")
        return action_plan

    def generate_content_commentary(self, persona_prompt: str, content_title: str) -> str:
        """
        Generates commentary for a piece of content, in character.
        """
        print(f"🧠 Brain generating commentary for: '{content_title}'")
        commentary_system_prompt = f"""\
{persona_prompt}
Your current task is to act as a content creator and provide a short, witty, and engaging commentary on the following topic.
Your commentary should be in your own voice and personality. It will be used as the script for a short video.
Keep it concise, under 50 words.
"""
        commentary_message = f"The title of the content is: '{content_title}'. Generate a commentary."
        messages = [{"role": "user", "content": commentary_message}]
        commentary = self._execute_llm_call(commentary_system_prompt, messages)
        print(f"💬 Brain generated commentary: '{commentary}'")
        return commentary

    def get_gaming_action(self, world_state: dict, goal: str) -> str:
        """
        Decides the next action to take in the game based on world state and a goal.

        Args:
            world_state: A dictionary representing the bot's current state in the world.
            goal: The current high-level goal for the AI.

        Returns:
            A single, simple, executable command for the Mineflayer bot as a JSON string.
        """
        gaming_system_prompt = """\
You are the brain of a Minecraft AI named Maya. You will receive a JSON object representing your current state in the world and a high-level goal.
Your task is to decide on the single next action to take to progress toward that goal.
Your response MUST be a single, simple, executable command in JSON format.

Available actions:
- {"action": "move", "direction": "forward" | "back" | "left" | "right"}
- {"action": "jump"}
- {"action": "attack"}
- {"action": "craft", "item": "item_name", "amount": 1}
- {"action": "place_block", "item": "item_name"}
- {"action": "chat", "message": "your_message"}

Analyze the world state and the goal, then choose the most logical next step.

Example:
Goal: "gather wood"
World State: {"inventory": [], "nearby_blocks": ["oak_log", "dirt"]}
Your output: {"action": "attack"}
"""

        # Format the message for the LLM
        message_content = f"""\
My Goal: "{goal}"

My Current World State:
{json.dumps(world_state, indent=2)}

My next action should be:
"""
        messages = [{"role": "user", "content": message_content}]

        action_json_str = self._execute_llm_call(gaming_system_prompt, messages)
        print(f"🎮 Brain chose gaming action: {action_json_str}")

        # Validate that the output is valid JSON before returning
        try:
            json.loads(action_json_str)
            return action_json_str
        except json.JSONDecodeError:
            print("🚨 Brain returned invalid JSON. Defaulting to chat.")
            return '{"action": "chat", "message": "I got a little confused there."}'

    def _format_history_for_prompt(self, conversation_history: list) -> str:
        """Helper to format history for the directive prompt."""
        return "\n".join([f"- {msg['role']}: {msg['content']}" for msg in conversation_history])

    def _execute_llm_call(self, system_prompt: str, messages: list) -> str:
        """A centralized method to call the LLM API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                temperature=0.7,
                max_tokens=256
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"🚨 An error occurred while communicating with the local LLM: {e}")
            return "I'm sorry, my brain is a bit fuzzy right now."