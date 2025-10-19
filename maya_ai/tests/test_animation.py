import unittest
from unittest.mock import MagicMock, patch
from maya_ai.personas.sarjana import Sarjana
from maya_ai.brain.core import Brain
from maya_ai.memory.database import MemoryDatabase
from maya_ai.tts.tts_manager import TTSManager

class TestAnimationSystem(unittest.TestCase):

    def setUp(self):
        """Set up mock objects for all external services."""
        self.mock_brain = MagicMock(spec=Brain)
        self.mock_memory = MagicMock(spec=MemoryDatabase)
        self.mock_tts = MagicMock(spec=TTSManager)
        self.user_id = 1

    @patch('maya_ai.personas.persona.Storyboarder')
    @patch('maya_ai.personas.persona.ImageGenerator')
    @patch('maya_ai.personas.persona.Animator')
    @patch('maya_ai.personas.persona.VideoEditor')
    def test_episode_creation_directive(self, MockVideoEditor, MockAnimator, MockImageGenerator, MockStoryboarder):
        """Tests the full pipeline of the episode creation directive."""
        # --- Mocks Setup ---
        mock_storyboarder_instance = MockStoryboarder.return_value
        mock_image_gen_instance = MockImageGenerator.return_value
        mock_animator_instance = MockAnimator.return_value
        mock_video_editor_instance = MockVideoEditor.return_value

        # The brain returns a plan to create an episode
        self.mock_brain.process_directive.return_value = "[PLAN: create_episode, prompt friendship]"
        # The brain writes a simple script
        self.mock_brain.write_episode_script.return_value = """
        [SCENE_START]
        SCENE_DESCRIPTION: Sarjana and Durjana in a sunny field.
        SARJANA: Isn't it a beautiful day, sister?
        DURJANA: It's okay, I guess.
        [SCENE_END]
        """
        # The storyboarder parses the script
        mock_storyboarder_instance.parse_script.return_value = [{
            'description': 'Sarjana and Durjana in a sunny field.',
            'dialogue': {'SARJANA': "Isn't it a beautiful day, sister?", 'DURJANA': "It's okay, I guess."}
        }]
        # The image generator returns a path
        mock_image_gen_instance.generate_image.return_value = "test_scene.png"
        # The animator returns a path
        mock_animator_instance.animate_lip_sync.return_value = "test_clip.mp4"

        # --- Execution ---
        sarjana = Sarjana(self.mock_brain, self.mock_memory, self.user_id, self.mock_tts)
        sarjana.storyboarder = mock_storyboarder_instance
        sarjana.image_generator = mock_image_gen_instance
        sarjana.animator = mock_animator_instance
        sarjana.video_editor = mock_video_editor_instance

        final_message = sarjana.execute_directive("create an episode about friendship")

        # --- Assertions ---
        self.mock_brain.write_episode_script.assert_called_once_with("friendship")
        mock_storyboarder_instance.parse_script.assert_called_once()
        mock_image_gen_instance.generate_image.assert_called_once()
        # Should be called twice, once for each character's dialogue
        self.assertEqual(self.mock_tts.speak.call_count, 2)
        self.assertEqual(mock_animator_instance.animate_lip_sync.call_count, 2)
        mock_video_editor_instance.stitch_videos.assert_called_once()
        self.assertIn("I've finished the new episode!", final_message)

if __name__ == "__main__":
    unittest.main()