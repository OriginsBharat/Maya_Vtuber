from maya_ai.brain.core import Brain
from maya_ai.personas.persona import Persona
from maya_ai.config.config_loader import get_config
from maya_ai.skills.skill_manager import SkillManager
from loguru import logger
import os
import json
from typing import Tuple, List, Dict, Any

class Orchestrator:
    """
    Manages the interaction between the personas, skills, and the UI.
    """
    def __init__(self):
        """
        Initializes the Orchestrator, ConfigManager, and all core components.
        """
        try:
            self.config = get_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}", exc_info=True)
            raise

        self.brain = Brain()
        self.skill_manager = SkillManager()

        sarjana_prompt_file = self.config.get('personas', {}).get('sarjana', {}).get('prompt_file')
        self.sarjana = Persona(name="Sarjana", brain=self.brain, persona_prompt_file=sarjana_prompt_file)

        durjana_prompt_file = self.config.get('personas', {}).get('durjana', {}).get('prompt_file')
        self.durjana = Persona(name="Durjana", brain=self.brain, persona_prompt_file=durjana_prompt_file)

        logger.info("Orchestrator initialized successfully.")

    def run_interaction_cycle(self, simulated_chat: List[str], hint: str = None, goal: str = None) -> Tuple[str, str]:
        """
        Runs a single cycle of interaction based on chat and an optional hint.
        """
        logger.info(f"Running interaction cycle with chat: {simulated_chat}, hint: {hint}, goal: {goal}")

        directive = self._parse_directive(simulated_chat, hint)
        skill_choice = self._choose_skill(directive)

        try:
            skill_name, action_name, args = skill_choice

            if skill_name == "ask_creator":
                question = args.get("question")
                logger.info(f"AI is asking for help: {question}")
                hint = input(f"Maya is asking: {question}\nYour response: ")
                return self.run_interaction_cycle(simulated_chat, hint, goal)

            result = self._execute_skill(skill_name, action_name, args, goal)
            return self._generate_responses(result)

        except json.JSONDecodeError:
            logger.error(f"The brain returned an invalid JSON response: {skill_choice}", exc_info=True)
            return "Error: The brain returned an invalid JSON response.", ""
        except Exception as e:
            logger.error(f"An unexpected error occurred in interaction cycle: {e}", exc_info=True)
            return f"An unexpected error occurred: {e}", ""

    def _parse_directive(self, simulated_chat: List[str], hint: str) -> str:
        chat_summary = self._generate_chat_summary(simulated_chat)
        return f"{chat_summary}\n{hint}"

    def _choose_skill(self, directive: str) -> Tuple[str, str, Dict[str, Any]]:
        skills = self._get_available_skills()
        chosen_skill_json = self.brain.choose_skill(directive, skills)
        chosen_skill = json.loads(chosen_skill_json)
        return chosen_skill.get("skill"), chosen_skill.get("action"), chosen_skill.get("args", {})

    def _execute_skill(self, skill_name: str, action_name: str, args: Dict[str, Any], goal: str) -> Any:
        skill = self.skill_manager.get_skill(skill_name)
        if not skill:
            logger.error(f"Skill '{skill_name}' not found.")
            return f"Error: Skill '{skill_name}' not found."

        if skill_name == "Minecraft Skill" and goal:
            world_state = skill.perform_action("get_world_state")
            action_json = self.brain.get_gaming_action(world_state, goal)
            action = json.loads(action_json)
            return skill.perform_action("game_action", action=action)
        else:
            return skill.perform_action(action_name, **args)

    def _generate_responses(self, result: Any) -> Tuple[str, str]:
        logger.info(f"Generating responses based on result: {result}")
        sarjana_prompt = f"Action result: {result}"
        sarjana_response = self.sarjana.think(sarjana_prompt.strip())

        durjana_prompt = f"Action result: {result}\nSarjana said: '{sarjana_response}'"
        durjana_response = self.durjana.think(durjana_prompt.strip())

        self.sarjana.clear_history()
        self.durjana.clear_history()

        return sarjana_response, durjana_response

    def _generate_chat_summary(self, chat_messages: list) -> str:
        if not chat_messages:
            return "The chat is quiet."
        return " ".join(str(m) for m in chat_messages)

    def _get_available_skills(self) -> list:
        skill_list = []
        for skill_name in self.skill_manager.get_skill_names():
            skill = self.skill_manager.get_skill(skill_name)
            skill_info = {
                "name": skill.get_name(),
                "actions": skill.get_possible_actions()
            }
            skill_list.append(skill_info)
        return skill_list
