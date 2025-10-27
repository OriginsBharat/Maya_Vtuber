from maya_ai.brain.core import Brain
from maya_ai.memory.memory_manager import MemoryManager
from maya_ai.config.config_manager import ConfigManager
import uuid

class Persona:
    """
    Represents a single AI persona, with its own personality, memory, and voice.
    """
    def __init__(self, brain: Brain, name: str, system_prompt: str, config_manager: ConfigManager):
        """
        Initializes a Persona.
        """
        self.brain = brain
        self.name = name
        self.system_prompt = system_prompt
        self.conversation_history = []
        # The MemoryManager now requires the ConfigManager
        self.memory = MemoryManager(persona_name=name, config_manager=config_manager)

    def think(self, incoming_message: str) -> str:
        # (This logic remains the same as the previous memory-enabled version)
        recalled_memories = self.memory.recall_memories(query_text=incoming_message, num_memories=3)
        memory_context = "\n".join(recalled_memories)

        self.add_to_history("user", incoming_message)

        contextual_prompt = f"""
        Relevant memories:
        <memories>
        {memory_context}
        </memories>
        Respond to the latest message based on these memories.
        """

        full_history_for_llm = [{"role": "system", "content": self.system_prompt + "\n" + contextual_prompt}] + self.conversation_history

        response = self.brain.get_response(full_history_for_llm)

        self.add_to_history("assistant", response)

        return response

    def add_to_history(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        self.memory.add_memory(f"{role}: {content}")

    def clear_history(self):
        self.conversation_history = []
