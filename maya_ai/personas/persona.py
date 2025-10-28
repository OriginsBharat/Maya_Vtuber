from maya_ai.brain.core import Brain
from maya_ai.memory.memory_manager import MemoryManager
from maya_ai.config.config_loader import get_config
from loguru import logger
import uuid

class Persona:
    """
    Represents a single AI persona, with its own personality, memory, and voice.
    """
    def __init__(self, brain: Brain, name: str, system_prompt: str):
        """
        Initializes a Persona.
        """
        self.brain = brain
        self.name = name
        self.system_prompt = system_prompt
        self.conversation_history = []
        self.memory = MemoryManager(persona_name=name)
        logger.info(f"Persona '{self.name}' initialized.")

    def think(self, incoming_message: str) -> str:
        logger.info(f"'{self.name}' is thinking about: {incoming_message}")
        recalled_facts = self.memory.recall_facts(query=incoming_message)
        memory_context = "\n".join(recalled_facts)

        self.add_to_history("user", incoming_message)

        contextual_prompt = f"""
        Relevant facts:
        <facts>
        {memory_context}
        </facts>
        Respond to the latest message based on these facts and the conversation history.
        """

        response = self.brain.get_response(self.system_prompt + "\n" + contextual_prompt, self.conversation_history)

        self.add_to_history(self.name, response)

        return response

    def add_to_history(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        self.memory.add_conversation_turn(speaker=role, text=content)

    def clear_history(self):
        self.conversation_history = []
        logger.info(f"Conversation history for '{self.name}' cleared.")
