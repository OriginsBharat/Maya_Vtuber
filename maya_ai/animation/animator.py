import shutil
from loguru import logger

class Animator:
    """
    Handles the lip-sync animation of a character.
    """
    def __init__(self):
        logger.info("👄 Animator initialized.")

    def animate_lip_sync(self, character_image_path: str, dialogue_audio_path: str, output_path: str = "lip_sync_video.mp4"):
        """
        Creates a lip-synced video from a character image and dialogue audio.

        Args:
            character_image_path: Path to the static image of the character.
            dialogue_audio_path: Path to the dialogue audio file.
            output_path: Path to save the final animated video.

        Returns:
            The path to the saved video, or None on error.
        """
        logger.info("Simulating lip-sync animation...")
        logger.info(f"Character: {character_image_path}, Dialogue: {dialogue_audio_path}")

        try:
            from maya_ai.video.editor import VideoEditor
            editor = VideoEditor()
            result_path = editor.create_video(character_image_path, dialogue_audio_path, output_path)

            if result_path:
                logger.info(f"✅ Simulated lip-sync video created at '{output_path}'")
                return result_path
            else:
                raise RuntimeError("Video creation failed during simulated lip-sync.")

        except Exception as e:
            logger.error(f"🚨 An error occurred during simulated animation: {e}", exc_info=True)
            return None
