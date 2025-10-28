import ollama
import base64
from maya_ai.skills.skill import Skill
from loguru import logger

class VisualSenseSkill(Skill):
    def __init__(self):
        self.model = "llava"

    def get_name(self) -> str:
        return "Visual Sense Skill"

    def get_possible_actions(self) -> list:
        return [
            {
                "name": "analyze_image",
                "description": "Analyzes an image and answers a question about it.",
                "args": {"image_path": "string", "prompt": "string"}
            }
        ]

    def perform_action(self, action_name: str, **kwargs) -> str:
        if action_name == "analyze_image":
            image_path = kwargs.get("image_path")
            prompt = kwargs.get("prompt")
            if not image_path or not prompt:
                logger.error("image_path and prompt are required for analyze_image action.")
                return "Error: image_path and prompt are required."
            return self._analyze_image(image_path, prompt)
        logger.warning(f"Unknown action for Visual Sense Skill: {action_name}")
        return f"Unknown action: {action_name}"

    def _analyze_image(self, image_path: str, prompt: str) -> str:
        try:
            logger.info(f"Analyzing image: {image_path} with prompt: '{prompt}'")
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [encoded_string]
                    }
                ]
            )
            logger.info("Image analysis successful.")
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error analyzing image: {e}", exc_info=True)
            return f"Error analyzing image: {e}"

def create_skill():
    return VisualSenseSkill()
