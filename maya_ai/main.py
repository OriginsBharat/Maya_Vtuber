from maya_ai.config.config_loader import get_config
from maya_ai.orchestrator import Orchestrator
from maya_ai.gaming_orchestrator import GamingOrchestrator
from maya_ai.proactive_orchestrator import ProactiveOrchestrator
from maya_ai.tts.tts_manager import TTSManager
from maya_ai.vtube.vts_manager import VTSManager
from maya_ai.ui.gradio_app import launch_ui
from loguru import logger
import os
import soundfile as sf
import numpy as np

# --- Global Objects ---
# These are initialized here and imported by the handlers to avoid circular dependencies.
config = get_config()
orchestrator = Orchestrator()
gaming_orchestrator = GamingOrchestrator(orchestrator.brain, orchestrator.skill_manager)
proactive_orchestrator = ProactiveOrchestrator(orchestrator.brain, orchestrator.skill_manager, {"Sarjana": orchestrator.sarjana, "Durjana": orchestrator.durjana})
tts_manager = TTSManager()
vts_manager = VTSManager()
mc_skill = orchestrator.skill_manager.get_skill("Minecraft Skill")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SARJANA_REF = os.path.join(BASE_DIR, config.get('tts', 'voice_references', {}).get('sarjana', 'voices/sarjana_ref.wav'))
DURJANA_REF = os.path.join(BASE_DIR, config.get('tts', 'voice_references', {}).get('durjana', 'voices/durjana_ref.wav'))

def main():
    """
    Main entry point for the Maya AI application.
    """
    # --- Logging Setup ---
    logger.add(
        config.get('logging', 'file'),
        level=config.get('logging', 'level'),
        rotation="10 MB",
        retention="5 days"
    )

    # --- Ensure Voice Reference Files Exist ---
    if not os.path.exists(SARJANA_REF):
        logger.warning(f"Sarjana voice reference not found at {SARJANA_REF}. Creating a dummy file.")
        sf.write(SARJANA_REF, np.zeros(16000, dtype=np.int16), 16000)
    if not os.path.exists(DURJANA_REF):
        logger.warning(f"Durjana voice reference not found at {DURJANA_REF}. Creating a dummy file.")
        sf.write(DURJANA_REF, np.zeros(16000, dtype=np.int16), 16000)

    # --- Start Background Services ---
    proactive_orchestrator.start()

    # --- Launch the UI ---
    launch_ui(config, vts_manager)

if __name__ == "__main__":
    main()
