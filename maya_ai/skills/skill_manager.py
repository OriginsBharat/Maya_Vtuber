from maya_ai.skills.skill import Skill
import os
import importlib
from maya_ai.config.config_loader import get_config
from loguru import logger

class SkillManager:
    """
    Manages the loading and execution of different skill plugins.
    """
    def __init__(self, brain):
        self.skills = {}
        self.brain = brain
        self.config = get_config()
        self._load_skills()

    def _load_skills(self):
        """
        Dynamically loads all skill plugins from the 'skills' directory.
        """
        skills_dir = os.path.dirname(__file__)
        for filename in os.listdir(skills_dir):
            if filename.endswith('_skill.py'):
                module_name = f"maya_ai.skills.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, 'create_skill'):
                        # Pass the brain instance to the skill creation function
                        skill_instance = module.create_skill(self.brain)
                        if isinstance(skill_instance, Skill):
                            skill_name = skill_instance.get_name()
                            self.skills[skill_name] = skill_instance
                            logger.info(f"Successfully loaded skill: {skill_name}")
                except Exception as e:
                    logger.error(f"Failed to load skill from {module_name}: {e}", exc_info=True)

    def get_skill_names(self) -> list:
        """
        Returns a list of all loaded skill names.
        """
        return list(self.skills.keys())

    def get_skill(self, skill_name: str) -> Skill:
        """
        Retrieves a loaded skill instance.
        """
        return self.skills.get(skill_name)
