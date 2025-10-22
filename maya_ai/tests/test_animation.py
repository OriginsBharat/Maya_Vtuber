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

    @patch('maya_ai.personas.persona.VideoEditor')
    @patch('maya_ai.personas.persona.LipSync')
    @patch('maya_ai.personas.persona.MotionGenerator')
    @patch('maya_ai.personas.persona.ImageGenerator')
    @patch('maya_ai.personas.persona.Storyboarder')
    @patch('maya_ai.personas.persona.CharacterManager')
    def test_full_episode_creation_pipeline(self, MockCharacterManager, MockStoryboarder, MockImageGenerator, MockMotionGenerator, MockLipSync, MockVideoEditor):
        """
        Tests the entire advanced animation pipeline from a single directive.
        """
        # --- Mocks Setup ---
        mock_storyboarder = MockStoryboarder.return_value
        mock_image_gen = MockImageGenerator.return_value
        mock_char_manager = MockCharacterManager.return_value
        mock_lip_sync = MockLipSync.return_value
        mock_motion_gen = MockMotionGenerator.return_value
        mock_video_editor = MockVideoEditor.return_value

        # Brain generates the plan and the script
        self.mock_brain.process_directive.return_value = "[PLAN: create_episode, prompt friendship]"
        self.mock_brain.write_episode_script.return_value = """
        [SCENE_START]
        [BACKGROUND: A sunny park.]
        [SARJANA: POSE=happy, DIALOGUE=Hello!]
        [ACTION: Durjana waves.]
        [SCENE_END]
        """

        # Storyboarder parses the script
        mock_storyboarder.parse_script.return_value = [
            {'type': 'dialogue', 'background': 'A sunny park.', 'character': 'SARJANA', 'pose': 'happy', 'dialogue': 'Hello!'},
            {'type': 'action', 'background': 'A sunny park.', 'description': 'Durjana waves.'}
        ]

        # Other mocks return successful paths
        mock_image_gen.generate_image.return_value = "bg.png"
        mock_char_manager.get_character_image.return_value = "char.png"
        mock_lip_sync.generate_lip_sync_data.return_value = [{'start': 0, 'end': 1, 'value': 'A'}]
        mock_video_editor.composite_shot.return_value = "shot1.mp4"

        # --- Execution ---
        sarjana = Sarjana(self.mock_brain, self.mock_memory, self.user_id, self.mock_tts)
        # We need to replace the real service instances on the persona with our mocks
        sarjana.storyboarder = mock_storyboarder
        sarjana.image_generator = mock_image_gen
        sarjana.character_manager = mock_char_manager
        sarjana.lip_sync = mock_lip_sync
        sarjana.motion_generator = mock_motion_gen
        sarjana.video_editor = mock_video_editor

        sarjana.execute_directive("create an episode about friendship")

        # --- Assertions ---
        self.mock_brain.write_episode_script.assert_called_once_with("friendship")
        mock_storyboarder.parse_script.assert_called_once()
        self.assertEqual(mock_image_gen.generate_image.call_count, 2)
        mock_char_manager.get_character_image.assert_called_once()
        self.mock_tts.speak.assert_called_once()
        mock_lip_sync.generate_lip_sync_data.assert_called_once()
        mock_video_editor.composite_shot.assert_called_once()
        mock_video_editor.stitch_videos.assert_called_once()

if __name__ == "__main__":
    unittest.main()