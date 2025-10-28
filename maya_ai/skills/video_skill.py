from moviepy.editor import *
from maya_ai.skills.skill import Skill
from loguru import logger

class VideoSkill(Skill):
    def get_name(self) -> str:
        return "Video Skill"

    def get_possible_actions(self) -> list:
        return [
            {
                "name": "create_video_from_text",
                "description": "Creates a video from a text clip.",
                "args": {"text": "string", "output_path": "string"}
            }
        ]

    def perform_action(self, action_name: str, **kwargs) -> str:
        if action_name == "create_video_from_text":
            text = kwargs.get("text")
            output_path = kwargs.get("output_path")
            if not text or not output_path:
                logger.error("text and output_path are required for create_video_from_text action.")
                return "Error: text and output_path are required."
            return self._create_video_from_text(text, output_path)
        logger.warning(f"Unknown action for Video Skill: {action_name}")
        return f"Unknown action: {action_name}"

    def _create_video_from_text(self, text: str, output_path: str) -> str:
        try:
            logger.info(f"Creating video from text: '{text}'")
            txt_clip = TextClip(text, fontsize=70, color='white')
            txt_clip = txt_clip.set_pos('center').set_duration(10)
            video = CompositeVideoClip([txt_clip])
            video.write_videofile(output_path, fps=24)
            logger.info(f"Video created successfully at {output_path}")
            return f"Video created at {output_path}"
        except Exception as e:
            logger.error(f"Error creating video: {e}", exc_info=True)
            return f"Error creating video: {e}"

def create_skill():
    return VideoSkill()
