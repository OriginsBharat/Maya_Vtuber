from maya_ai.brain.core import Brain
from maya_ai.memory.memory_manager import MemoryManager
import uuid

class Persona:
    """
    Represents a single AI persona, with its own personality, memory, and voice.
    """
    def __init__(self, brain: Brain, name: str, system_prompt: str):
        """
        Initializes a Persona.

        Args:
            brain: The core Brain instance for LLM communication.
            name: The name of the persona (e.g., "Sarjana").
            system_prompt: The detailed instructions defining the persona's character.
        """
        self.brain = brain
        self.name = name
        self.system_prompt = system_prompt
        self.conversation_history = []
        self.memory = MemoryManager(persona_name=name)

    def think(self, incoming_message: str) -> str:
        """
        Generates a response based on the current conversation and long-term memory.

        Args:
            incoming_message: The latest message or prompt for the persona to respond to.
        """
        # Recall relevant memories
        recalled_memories = self.memory.recall_memories(query_text=incoming_message, num_memories=3)
        memory_context = "\n".join(recalled_memories)

        # Add the incoming message to short-term history
        self.add_to_history("user", incoming_message)

        # Construct a prompt that includes the memories
        prompt_with_memory = f"""
        Here are some relevant memories from your past:
        <memories>
        {memory_context}
        </memories>

        Based on these memories and our current conversation, please respond to the latest message.
        """

        # We add the memory context as a new system-level instruction for this turn
        full_conversation_history = self.conversation_history + [{"role": "system", "content": prompt_with_memory}]

        response = self.brain.get_response(self.system_prompt, full_conversation_history)

        # Add the AI's own response to its short-term history and long-term memory
        self.add_to_history("assistant", response)

        return response

    def add_to_history(self, role: str, content: str):
        """
        Adds a message to the persona's conversation history and long-term memory.

        Args:
            role: The role of the message sender ('user' or 'assistant').
            content: The content of the message.
        """
        # Add to short-term conversation history
        self.conversation_history.append({"role": role, "content": content})

        # Also save it to long-term memory
        memory_id = str(uuid.uuid4())
        self.memory.add_memory(f"{role}: {content}", memory_id)

    def clear_history(self):
        """
        Clears the persona's short-term conversation history.
        Note: This does not clear the long-term vector memory.
        """
        self.conversation_history = []
