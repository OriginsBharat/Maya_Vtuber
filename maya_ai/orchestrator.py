from maya_ai.brain.core import Brain
from maya_ai.personas.sarjana import create_sarjana
from maya_ai.personas.durjana import create_durjana
from maya_ai.config.config_manager import ConfigManager

class Orchestrator:
    """
    Manages the interaction between the personas, skills, and the UI.
    """
    def __init__(self):
        """
        Initializes the Orchestrator, ConfigManager, and all core components.
        """
        try:
            # The ConfigManager is now the entry point for all secrets
            self.config_manager = ConfigManager()
        except ValueError as e:
            # If the Supabase keys are not set, we cannot proceed.
            raise RuntimeError(f"Failed to initialize ConfigManager: {e}. Please set SUPABASE_URL and SUPABASE_KEY.") from e

        self.brain = Brain()

        # Pass the ConfigManager to the persona creation so it can be used by the memory system
        self.sarjana = create_sarjana(self.brain, self.config_manager)
        self.durjana = create_durjana(self.brain, self.config_manager)

    def run_interaction_cycle(self, simulated_chat: list, hint: str = None):
        """
        Runs a single cycle of interaction based on chat and an optional hint.
        """
        chat_summary = self._generate_chat_summary(simulated_chat)

        hint_text = f"Director's Hint: '{hint}'" if hint else ""

        sarjana_prompt = f"Chat Summary: {chat_summary}\n{hint_text}"
        sarjana_response = self.sarjana.think(sarjana_prompt.strip())

        durjana_prompt = f"Chat Summary: {chat_summary}\nSarjana said: '{sarjana_response}'\n{hint_text}"
        durjana_response = self.durjana.think(durjana_prompt.strip())

        self.sarjana.clear_history()
        self.durjana.clear_history()

        return sarjana_response, durjana_response

    def _generate_chat_summary(self, chat_messages: list) -> str:
        if not chat_messages:
            return "The chat is quiet."
        # For now, just return the first message. A real implementation would summarize.
        return f"The latest message is: '{chat_messages[0]}'"
