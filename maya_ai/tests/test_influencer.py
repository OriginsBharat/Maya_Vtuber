import unittest
from unittest.mock import MagicMock, patch
from maya_ai.personas.sarjana import Sarjana
from maya_ai.brain.core import Brain
from maya_ai.memory.database import MemoryDatabase
from maya_ai.tts.tts_manager import TTSManager

class TestInfluencerSystem(unittest.TestCase):

    def setUp(self):
        """Set up mock objects for all external services."""
        self.mock_brain = MagicMock(spec=Brain)
        self.mock_memory = MagicMock(spec=MemoryDatabase)
        self.mock_tts = MagicMock(spec=TTSManager)
        self.user_id = 1

    @patch('maya_ai.personas.persona.YouTubeUploader')
    def test_upload_directive(self, MockYouTubeUploader):
        """Tests the video upload directive."""
        mock_uploader_instance = MockYouTubeUploader.return_value
        mock_uploader_instance.upload_video.return_value = "dQw4w9WgXcQ" # A famous video ID

        sarjana = Sarjana(self.mock_brain, self.mock_memory, self.user_id, self.mock_tts)
        # Manually set the last video path for the test
        sarjana.last_video_path = "test_video.mp4"
        sarjana.last_video_commentary = "This is a test commentary."

        # Simulate the brain returning an upload plan
        self.mock_brain.process_directive.return_value = "[PLAN: upload_video, title My Test Video]"

        final_message = sarjana.execute_directive("upload the last video with title My Test Video")

        # Assert that the uploader was called correctly
        mock_uploader_instance.upload_video.assert_called_once_with(
            file_path="test_video.mp4",
            title="My Test Video",
            description="AI-generated video by Maya. Original commentary: This is a test commentary.",
            tags=["ai", "vtuber", "maya", "sarjana"]
        )

        # Assert the final message contains the video link
        self.assertIn("https://www.youtube.com/watch?v=dQw4w9WgXcQ", final_message)

    @patch('maya_ai.personas.persona.Translator')
    @patch('maya_ai.personas.persona.VideoEditor')
    def test_dubbing_directive(self, MockVideoEditor, MockTranslator):
        """Tests the video dubbing directive."""
        mock_translator_instance = MockTranslator.return_value
        mock_translator_instance.translate.return_value = "Translated commentary."
        mock_editor_instance = MockVideoEditor.return_value

        sarjana = Sarjana(self.mock_brain, self.mock_memory, self.user_id, self.mock_tts)
        sarjana.last_video_path = "test_video.mp4"
        sarjana.last_video_commentary = "Original commentary."

        # Simulate the brain returning a dubbing plan
        self.mock_brain.process_directive.return_value = "[PLAN: dub_video, lang es]"

        final_message = sarjana.execute_directive("dub the last video in spanish")

        # 1. Assert the translator was called
        mock_translator_instance.translate.assert_called_once_with("Original commentary.", "es")

        # 2. Assert the TTS was called with the translated text
        self.mock_tts.speak.assert_called_once_with(
            "Translated commentary.",
            "voices/sarjana.wav",
            output_path="temp_dub_es.wav",
            language="es"
        )

        # 3. Assert the video editor was called to replace the audio
        mock_editor_instance.replace_audio.assert_called_once()

        # 4. Assert the final message is correct
        self.assertIn("I've dubbed the video in es!", final_message)

if __name__ == "__main__":
    unittest.main()