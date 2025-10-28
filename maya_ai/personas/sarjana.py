from maya_ai.personas.persona import Persona
from maya_ai.brain.core import Brain
import os
from maya_ai.config.config_loader import get_config

def load_prompt():
    """Loads the persona prompt from the path specified in the config."""
    config = get_config()
    prompt_path = config.get('personas', 'sarjana', {}).get('prompt_file')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def create_sarjana(brain: Brain) -> Persona:
    """
    Creates the Sarjana persona instance.
    """
    return Persona(
        brain=brain,
        name="Sarjana",
        system_prompt=load_prompt()
    )
