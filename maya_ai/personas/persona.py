from maya_ai.brain.core import Brain
from maya_ai.memory.database import MemoryDatabase

class Persona:
    """
    Base class for all personas.
    Handles the interaction between the brain, memory, and the specific persona's characteristics.
    """
    def __init__(self, brain: Brain, memory: MemoryDatabase, user_id: int):
        self.brain = brain
        self.memory = memory
        self.user_id = user_id
        self.system_prompt = self._create_system_prompt()

    def _create_system_prompt(self) -> str:
        """
        Creates the detailed system prompt for the persona.
        This method MUST be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _create_system_prompt.")

    def generate_response(self, latest_message: str) -> str:
        """
        Generates a response from the persona.

        1. Retrieves conversation history from memory.
        2. Calls the brain to get a response, using the specific persona's system prompt.
        3. Logs the user's message and the AI's response to memory.

        Args:
            latest_message: The latest message from the user.

        Returns:
            The persona's response as a string.
        """
        # 1. Retrieve history
        history = self.memory.get_history(self.user_id)

        # 2. Get response from brain
        ai_response = self.brain.get_response(
            system_prompt=self.system_prompt,
            conversation_history=history,
            latest_message=latest_message
        )

        # 3. Log the interaction to memory
        self.memory.log_message(self.user_id, "user", latest_message)
        self.memory.log_message(self.user_id, "assistant", ai_response)

        return ai_response