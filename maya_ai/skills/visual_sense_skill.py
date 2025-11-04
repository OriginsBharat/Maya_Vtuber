from maya_ai.skills.skill import Skill
from maya_ai.config.config_loader import get_config
from loguru import logger
import mss
import os
from datetime import datetime

class VisualSenseSkill(Skill):
    """
    A skill that allows the AI to "see" by capturing and analyzing the screen.
    """
    def __init__(self, brain):
        self.brain = brain
        self.config = get_config()

    def get_name(self) -> str:
        return "Visual Sense Skill"

    def get_possible_actions(self) -> list:
        return [
            {
                "name": "analyze_screen",
                "description": "Captures the current screen, analyzes it with a multimodal AI, and returns a description of what it sees.",
                "args": {"prompt": "string"}
            }
        ]

    def perform_action(self, action_name: str, **kwargs) -> str:
        if action_name == "analyze_screen":
            prompt = kwargs.get("prompt", "Describe what you see on the screen.")
            return self._analyze_screen(prompt)

        logger.warning(f"Unknown action for Visual Sense Skill: {action_name}")
        return f"Unknown action: {action_name}"

    def _analyze_screen(self, prompt: str) -> str:
        """
        Captures the screen, passes it to the brain for analysis, and returns the result.
        """
        screenshot_path = self._capture_screen()
        if screenshot_path.startswith("Error:"):
            return screenshot_path

        # Call the brain's new multimodal method
        analysis_result = self.brain.see_and_think(prompt, screenshot_path)

        # Clean up the temporary screenshot file
        try:
            os.remove(screenshot_path)
            logger.info(f"Removed temporary screenshot: {screenshot_path}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary screenshot {screenshot_path}: {e}")

        return analysis_result

    def _capture_screen(self) -> str:
        """
        Captures the primary monitor and saves it to a temporary file.

        Returns:
            The file path to the captured screenshot, or an error message.
        """
        try:
            temp_path = self.config.get('paths', 'temp', 'temp/')
            os.makedirs(temp_path, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(temp_path, f"screenshot_{timestamp}.png")

            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=output_path)

            logger.info(f"Screen captured successfully to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to capture screen: {e}", exc_info=True)
            return f"Error: Failed to capture screen. {e}"

def create_skill(brain):
    return VisualSenseSkill(brain)
