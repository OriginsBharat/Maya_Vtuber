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

    def generate_response(self, latest_message: str, is_roleplay: bool = False) -> str:
        """
        Generates a standard conversational response from the persona.

        Args:
            latest_message: The latest message from the user.
            is_roleplay: Flag indicating if this is a private message from the director.

        Returns:
            The persona's response as a string.
        """
        history = self.memory.get_history(self.user_id)

        # Add context if it's a private roleplay message from the director
        if is_roleplay:
            latest_message = (
                f"(This is a private, in-character voice message from my creator, originsbharat. "
                f"I must respond to it lovingly and in-character.)\n\n{latest_message}"
            )

        ai_response = self.brain.get_response(
            system_prompt=self.system_prompt,
            conversation_history=history,
            latest_message=latest_message
        )

        # Log the interaction to memory
        self.memory.log_message(self.user_id, "user", latest_message)
        self.memory.log_message(self.user_id, "assistant", ai_response)

        return ai_response

    def execute_directive(self, directive: str) -> str:
        """
        Executes a high-level directive from the director.

        1. Gets the recent conversation history for context.
        2. Asks the brain to process the directive into a concrete action plan.
        3. Asks the persona to execute the action plan in character.
        4. Logs the final response to memory.

        Args:
            directive: The natural language directive.

        Returns:
            The persona's response after executing the directive.
        """
        history = self.memory.get_history(self.user_id)

        # Get the action plan from the brain
        action_plan = self.brain.process_directive(directive, history)

        # Create a new message for the persona to execute the plan
        execution_message = (
            f"(My creator, originsbharat, has given me a direct order. "
            f"I must follow this instruction exactly, but in my own unique voice and personality. "
            f"Instruction: '{action_plan}')"
        )

        # The persona "talks to itself" to generate the response based on the directive
        final_response = self.brain.get_response(
            system_prompt=self.system_prompt,
            conversation_history=history,
            latest_message=execution_message
        )

        # Log the directive and the response
        self.memory.log_message(self.user_id, "director", directive)
        self.memory.log_message(self.user_id, "assistant", final_response)

        return final_response