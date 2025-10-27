from maya_ai.personas.persona import Persona
from maya_ai.brain.core import Brain
from maya_ai.config.config_manager import ConfigManager
import os

def load_prompt():
    """Loads the persona prompt from the prompts directory."""
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'sarjana.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def create_sarjana(brain: Brain, config_manager: ConfigManager) -> Persona:
    """
    Creates the Sarjana persona instance.
    """
    return Persona(
        brain=brain,
        name="Sarjana",
        system_prompt=load_prompt(),
        config_manager=config_manager
    )
