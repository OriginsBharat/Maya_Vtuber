import unittest
from unittest.mock import MagicMock, patch
from maya_ai.personas.sarjana import Sarjana
from maya_ai.brain.core import Brain
from maya_ai.memory.database import MemoryDatabase
from maya_ai.tts.tts_manager import TTSManager

class TestCreatorSystem(unittest.TestCase):

    def setUp(self):
        """Set up mock objects for all external services."""
        self.mock_brain = MagicMock(spec=Brain)
        self.mock_memory = MagicMock(spec=MemoryDatabase)
        self.mock_tts = MagicMock(spec=TTSManager)
        self.user_id = 1

    @patch('maya_ai.personas.persona.WebScraper')
    @patch('maya_ai.personas.persona.VideoEditor')
    def test_video_creation_directive(self, MockVideoEditor, MockWebScraper):
        """
        Tests the full pipeline of the video creation directive,
        from the initial command to the final orchestration.
        """
        # --- Mocks Setup ---
        # Mock instances of the external services
        mock_scraper_instance = MockWebScraper.return_value
        mock_editor_instance = MockVideoEditor.return_value

        # The brain should return a multi-step plan
        self.mock_brain.process_directive.return_value = "[PLAN: scrape_content r/memes meme, generate_commentary, synthesize_audio, create_video]"

        # The scraper should return some mock content
        mock_scraper_instance.find_top_image_post.return_value = {
            "title": "Test Meme",
            "image_url": "http://example.com/meme.jpg",
            "post_url": "http://reddit.com/r/memes/123"
        }
        mock_scraper_instance.download_image.return_value = "mock_image.jpg"

        # The brain should generate commentary
        self.mock_brain.generate_content_commentary.return_value = "This is a funny meme."

        # The video editor should return the path to the final video
        mock_editor_instance.create_video.return_value = "final_video.mp4"

        # --- Execution ---
        # Instantiate the persona with the mocked components
        sarjana = Sarjana(self.mock_brain, self.mock_memory, self.user_id, self.mock_tts)
        # We need to replace the real service instances on the persona with our mocks
        sarjana.web_scraper = mock_scraper_instance
        sarjana.video_editor = mock_editor_instance

        directive = "create a video about memes from r/memes"
        final_message = sarjana.execute_directive(directive)

        # --- Assertions ---
        # 1. Assert the brain was called to create the plan
        self.mock_brain.process_directive.assert_called_once()

        # 2. Assert the scraper was called
        mock_scraper_instance.find_top_image_post.assert_called_once()
        mock_scraper_instance.download_image.assert_called_once()

        # 3. Assert the brain was called to generate commentary
        self.mock_brain.generate_content_commentary.assert_called_once_with(
            sarjana.system_prompt, "Test Meme"
        )

        # 4. Assert the TTS was called to speak the commentary
        self.mock_tts.speak.assert_called_once_with(
            "This is a funny meme.",
            "voices/sarjana.wav",
            output_path="temp_audio.wav"
        )

        # 5. Assert the video editor was called to create the final video
        mock_editor_instance.create_video.assert_called_once()

        # 6. Assert the final message is correct
        self.assertIn("I've finished creating the video!", final_message)

if __name__ == "__main__":
    unittest.main()