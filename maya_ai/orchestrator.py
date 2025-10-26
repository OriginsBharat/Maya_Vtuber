from maya_ai.brain.core import Brain
from maya_ai.personas.sarjana import create_sarjana
from maya_ai.personas.durjana import create_durjana

class Orchestrator:
    """
    Manages the interaction between the personas and the chat.
    """
    def __init__(self):
        """
        Initializes the Orchestrator and the personas.
        """
        self.brain = Brain()
        self.sarjana = create_sarjana(self.brain)
        self.durjana = create_durjana(self.brain)

    def generate_chat_summary(self, chat_messages: list) -> str:
        """
        (Placeholder for now) Generates a summary of recent chat messages.
        For the MVP, this will just return the first message.
        """
        if not chat_messages:
            return "The chat is quiet."
        # In the future, this will use another LLM call to summarize the chat.
        return f"The latest message in chat is: '{chat_messages[0]}'"

    def run_interaction_cycle(self, simulated_chat: list, hint: str = None):
        """
        Runs a single cycle of interaction based on chat and an optional hint.
        """
        chat_summary = self.generate_chat_summary(simulated_chat)

        # Incorporate the hint if it exists
        hint_text = f"Director's Hint for this interaction: '{hint}'. Please weave this into your response." if hint else ""

        # 1. Sarjana comments on the chat summary, guided by the hint.
        sarjana_prompt = f"Here is a summary of the chat activity: {chat_summary}\n\n{hint_text}"
        sarjana_response = self.sarjana.think(sarjana_prompt.strip())

        # 2. Durjana receives Sarjana's comment, the chat summary, and the hint, then responds.
        durjana_prompt = f"Chat summary: {chat_summary}\n\nSarjana just said this about it: '{sarjana_response}'.\n\n{hint_text}"
        durjana_response = self.durjana.think(durjana_prompt.strip())

        # Clear short-term history for the next cycle to keep interactions fresh
        self.sarjana.clear_history()
        self.durjana.clear_history()

        return sarjana_response, durjana_response
