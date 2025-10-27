from maya_ai.brain.core import Brain
from maya_ai.memory.memory_manager import MemoryManager
import uuid

class Persona:
    """
    Represents a single AI persona, with its own personality, memory, and voice.
    This is the corrected version that re-integrates the memory system.
    """
    def __init__(self, brain: Brain, name: str, system_prompt: str):
        self.brain = brain
        self.name = name
        self.system_prompt = system_prompt
        self.conversation_history = []
        self.memory = MemoryManager(persona_name=name)

    def think(self, incoming_message: str) -> str:
        # Recall relevant memories to add context to the prompt
        recalled_memories = self.memory.recall_memories(query_text=incoming_message, num_memories=3)
        memory_context = "\n".join(recalled_memories)

        # The user's direct message for this turn
        self.add_to_history("user", incoming_message)

        # We create a special system message for this turn that includes the memory context
        contextual_prompt = f"""
        Here are some relevant memories from your past that might inform your response:
        <memories>
        {memory_context}
        </memories>

        Based on these memories and our current conversation, please respond to the latest message.
        """

        # Combine the base system prompt with the contextual one for the LLM call
        full_history_for_llm = [{"role": "system", "content": self.system_prompt + "\n" + contextual_prompt}] + self.conversation_history

        response = self.brain.get_response(full_history_for_llm)

        # Add the AI's own response to its history and long-term memory
        self.add_to_history("assistant", response)

        return response

    def add_to_history(self, role: str, content: str):
        # Add to short-term (this session's) conversation history
        self.conversation_history.append({"role": role, "content": content})

        # Also save it to long-term, recallable memory
        memory_id = str(uuid.uuid4())
        self.memory.add_memory(f"{role}: {content}", memory_id)

    def clear_history(self):
        # Clears only the short-term conversation history
        self.conversation_history = []
