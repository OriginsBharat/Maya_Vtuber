from maya_ai.skills.skill import Skill
import os
import importlib

from maya_ai.config.config_manager import ConfigManager

class SkillManager:
    """
    Manages the loading and execution of different skill plugins.
    """
    def __init__(self, config_manager: ConfigManager):
        self.skills = {}
        self.config_manager = config_manager
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
                    # Assumes each skill file has a create_skill() function
                    if hasattr(module, 'create_skill'):
                        # Pass the config_manager to the create_skill function
                        skill_instance = module.create_skill(self.config_manager)
                        if isinstance(skill_instance, Skill):
                            skill_name = skill_instance.get_name()
                            self.skills[skill_name] = skill_instance
                            print(f"Successfully loaded skill: {skill_name}")
                except Exception as e:
                    print(f"Failed to load skill from {module_name}: {e}")

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
