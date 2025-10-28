from maya_ai.skills.skill import Skill

class OCRSkill(Skill):
    def get_name(self) -> str:
        return "OCR Skill"

    def get_possible_actions(self) -> list:
        return [
            {
                "name": "read_text_from_image",
                "description": "Reads text from an image file (placeholder).",
                "args": {"image_path": "string"}
            }
        ]

    def perform_action(self, action_name: str, **kwargs) -> str:
        if action_name == "read_text_from_image":
            return "OCR functionality is not yet implemented with Deepseek OCR."
        return f"Unknown action: {action_name}"

def create_skill(config_manager):
    return OCRSkill()
