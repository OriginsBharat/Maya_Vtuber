from maya_ai.brain.core import Brain
from maya_ai.personas.sarjana import create_sarjana
from maya_ai.personas.durjana import create_durjana
from maya_ai.config.config_manager import ConfigManager
from maya_ai.skills.skill_manager import SkillManager
import os

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
        self.skill_manager = SkillManager(self.config_manager)

        # Pass the ConfigManager to the persona creation so it can be used by the memory system
        self.sarjana = create_sarjana(self.brain, self.config_manager)
        self.durjana = create_durjana(self.brain, self.config_manager)

    def run_interaction_cycle(self, simulated_chat: list, hint: str = None, goal: str = None):
        """
        Runs a single cycle of interaction based on chat and an optional hint.
        """
        chat_summary = self._generate_chat_summary(simulated_chat)
        directive = f"{chat_summary}\n{hint}"

        skills = self._get_available_skills()
        chosen_skill_json = self.brain.choose_skill(directive, skills)

        try:
            chosen_skill = json.loads(chosen_skill_json)
            skill_name = chosen_skill.get("skill")
            action_name = chosen_skill.get("action")
            args = chosen_skill.get("args", {})

            if skill_name == "ask_creator":
                question = args.get("question")
                hint = input(f"Maya is asking: {question}\nYour response: ")
                return self.run_interaction_cycle(simulated_chat, hint, goal)

            skill = self.skill_manager.get_skill(skill_name)
            if not skill:
                return f"Error: Skill '{skill_name}' not found."

            if skill_name == "Minecraft Skill" and goal:
                world_state = skill.perform_action("get_world_state")
                action_json = self.brain.get_gaming_action(world_state, goal)
                action = json.loads(action_json)
                result = skill.perform_action("game_action", action=action)
            else:
                result = skill.perform_action(action_name, **args)

            sarjana_prompt = f"Action result: {result}"
            sarjana_response = self.sarjana.think(sarjana_prompt.strip())

            durjana_prompt = f"Action result: {result}\nSarjana said: '{sarjana_response}'"
            durjana_response = self.durjana.think(durjana_prompt.strip())

            self.sarjana.clear_history()
            self.durjana.clear_history()

            return sarjana_response, durjana_response

        except json.JSONDecodeError:
            return "Error: The brain returned an invalid JSON response."
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def _generate_chat_summary(self, chat_messages: list) -> str:
        if not chat_messages:
            return "The chat is quiet."
        return " ".join(str(m) for m in chat_messages)

    def _get_available_skills(self) -> list:
        """
        Gets the list of available skills from the SkillManager.
        """
        skill_list = []
        for skill_name in self.skill_manager.get_skill_names():
            skill = self.skill_manager.get_skill(skill_name)
            skill_info = {
                "name": skill.get_name(),
                "actions": skill.get_possible_actions()
            }
            skill_list.append(skill_info)
        return skill_list
