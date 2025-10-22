from maya_ai.brain.core import Brain
from maya_ai.memory.vector_memory import VectorMemory

class Persona:
    """
    A simplified base class for personas.
    Handles the interaction between the brain and memory, including RAG.
    """
    def __init__(self, brain: Brain, vector_memory: VectorMemory, system_prompt: str):
        self.brain = brain
        self.vector_memory = vector_memory
        self.system_prompt = system_prompt
        self.conversation_history = []
        self.conversation_turn_counter = 0
        self.summary_threshold = 10 # Summarize every 10 turns

    def generate_response(self, latest_message: str) -> str:
        """
        Generates a response, stores history, and triggers summarization.
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": latest_message})

        # Get response from brain
        ai_response = self.brain.get_response(
            system_prompt=self.system_prompt,
            conversation_history=self.conversation_history,
            latest_message=latest_message # The brain will add this to the messages list
        )

        # Add AI response to history
        self.conversation_history.append({"role": "assistant", "content": ai_response})

        # Handle conversation summarization
        self.conversation_turn_counter += 1
        if self.conversation_turn_counter >= self.summary_threshold:
            self._summarize_and_memorize()

        return ai_response

    def _summarize_and_memorize(self):
        """Summarizes the recent conversation and stores it in long-term memory."""
        print("--- Reached conversation summary threshold ---")

        # Get the last `summary_threshold` turns for summarization
        # Each turn is a user message and an assistant response, so 2 * threshold
        recent_turns = self.conversation_history[-(2 * self.summary_threshold):]

        summary = self.brain.summarize_conversation(recent_turns)
        self.vector_memory.add_memory(summary)

        # Reset counter
        self.conversation_turn_counter = 0
        print(f"Stored summary: '{summary[:50]}...'")