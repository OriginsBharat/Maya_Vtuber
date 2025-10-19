from maya_ai.brain.core import Brain
from maya_ai.memory.database import MemoryDatabase
from maya_ai.content.web_scraper import WebScraper
from maya_ai.tts.tts_manager import TTSManager
from maya_ai.video.editor import VideoEditor
from maya_ai.translation.translator import Translator
from maya_ai.socials.youtube_uploader import YouTubeUploader
from maya_ai.animation.storyboarder import Storyboarder
from maya_ai.animation.image_generator import ImageGenerator
from maya_ai.animation.animator import Animator
import re
from pathlib import Path

class Persona:
    """
    Base class for all personas.
    Handles the interaction between the brain, memory, and the specific persona's characteristics.
    """
    def __init__(self, brain: Brain, memory: MemoryDatabase, user_id: int, tts_manager: TTSManager):
        self.brain = brain
        self.memory = memory
        self.user_id = user_id
        self.tts_manager = tts_manager
        self.web_scraper = WebScraper()
        self.video_editor = VideoEditor()
        self.translator = Translator()
        self.youtube_uploader = YouTubeUploader()
        self.storyboarder = Storyboarder()
        self.image_generator = ImageGenerator()
        self.animator = Animator()
        self.system_prompt = self._create_system_prompt()
        self.last_video_path = None
        self.last_video_commentary = None

    def _create_system_prompt(self) -> str:
        """
        Creates the detailed system prompt for the persona.
        This method MUST be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _create_system_prompt.")

    def generate_response(self, latest_message: str, is_roleplay: bool = False) -> str:
        """
        Generates a standard conversational response from the persona.

        Args:
            latest_message: The latest message from the user.
            is_roleplay: Flag indicating if this is a private message from the director.

        Returns:
            The persona's response as a string.
        """
        history = self.memory.get_history(self.user_id)

        # Add context if it's a private roleplay message from the director
        if is_roleplay:
            latest_message = (
                f"(This is a private, in-character voice message from my creator, originsbharat. "
                f"I must respond to it lovingly and in-character.)\n\n{latest_message}"
            )

        ai_response = self.brain.get_response(
            system_prompt=self.system_prompt,
            conversation_history=history,
            latest_message=latest_message
        )

        # Log the interaction to memory
        self.memory.log_message(self.user_id, "user", latest_message)
        self.memory.log_message(self.user_id, "assistant", ai_response)

        return ai_response

    def execute_directive(self, directive: str) -> str:
        """
        Executes a high-level directive from the director.

        1. Gets the recent conversation history for context.
        2. Asks the brain to process the directive into a concrete action plan.
        3. Asks the persona to execute the action plan in character.
        4. Logs the final response to memory.

        Args:
            directive: The natural language directive.

        Returns:
            The persona's response after executing the directive.
        """
        history = self.memory.get_history(self.user_id)

        # Get the action plan from the brain
        action_plan_str = self.brain.process_directive(directive, history)

        # Check for the type of plan
        if "scrape_content" in action_plan_str:
            return self._execute_video_creation_plan(action_plan_str)
        elif "upload_video" in action_plan_str:
            return self._execute_upload_plan(action_plan_str)
        elif "dub_video" in action_plan_str:
            return self._execute_dubbing_plan(action_plan_str)
        elif "create_episode" in action_plan_str:
            return self._execute_episode_creation_plan(action_plan_str)
        else:
            # It's a simple, single-step action
            return self._execute_simple_action(action_plan_str, history, directive)

    def _execute_simple_action(self, action_plan: str, history: list, directive: str) -> str:
        """Executes a simple, single-line action plan."""
        execution_message = (
            f"(My creator, originsbharat, has given me a direct order. "
            f"I must follow this instruction exactly, but in my own unique voice and personality. "
            f"Instruction: '{action_plan}')"
        )
        final_response = self.brain.get_response(
            system_prompt=self.system_prompt,
            conversation_history=history,
            latest_message=execution_message
        )
        self.memory.log_message(self.user_id, "director", directive)
        self.memory.log_message(self.user_id, "assistant", final_response)
        return final_response

    def _execute_video_creation_plan(self, plan_str: str) -> str:
        """Orchestrates the entire video creation workflow."""
        print("🎬 Persona is executing a video creation plan...")

        # --- 1. Scrape Content ---
        # A simple parser for our plan format, e.g., "[PLAN: scrape_content r/memes cats, ...]"
        match = re.search(r"scrape_content\s+([\w/]+)\s+(\w+)", plan_str)
        if not match:
            return "I'm sorry, I couldn't understand the video creation plan."

        subreddit, keyword = match.groups()
        content = self.web_scraper.find_top_image_post(subreddit or keyword)
        if not content:
            return f"I couldn't find any good content for '{subreddit or keyword}'."

        # --- 2. Download Image ---
        image_path = self.web_scraper.download_image(content["image_url"], "temp_image.jpg")
        if not image_path:
            return "I had trouble downloading the image for the video."

        # --- 3. Generate Commentary ---
        commentary = self.brain.generate_content_commentary(self.system_prompt, content["title"])

        # --- 4. Synthesize Audio ---
        voice_prompt = f"voices/{self.__class__.__name__.lower()}.wav"
        audio_path = "temp_audio.wav"
        self.tts_manager.speak(commentary, voice_prompt, output_path=audio_path)

        # --- 5. Create Video ---
        video_output_path = f"output_{content['title'].replace(' ', '_')[:20]}.mp4"
        self.video_editor.create_video(image_path, audio_path, video_output_path)

        # --- 6. Cleanup ---
        Path(image_path).unlink(missing_ok=True)
        Path(audio_path).unlink(missing_ok=True)

        final_message = f"I've finished creating the video! You can find it at '{video_output_path}'"
        print(f"✅ {final_message}")
        self.memory.log_message(self.user_id, "assistant", final_message)
        self.last_video_path = video_output_path
        self.last_video_commentary = commentary
        return final_message

    def _execute_upload_plan(self, plan_str: str) -> str:
        """Executes the plan to upload the last created video."""
        print("⬆️ Persona is executing an upload plan...")
        if not self.last_video_path:
            return "I haven't created a video yet. I need to create one first."

        match = re.search(r"title\s+([^,\]]+)", plan_str, re.IGNORECASE)
        if not match:
            return "I need a title to upload the video."

        title = match.group(1).strip()
        description = f"AI-generated video by Maya. Original commentary: {self.last_video_commentary}"

        video_id = self.youtube_uploader.upload_video(
            file_path=self.last_video_path,
            title=title,
            description=description,
            tags=["ai", "vtuber", "maya", self.__class__.__name__.lower()]
        )

        if video_id:
            return f"I've successfully uploaded the video! You can watch it here: https://www.youtube.com/watch?v={video_id}"
        else:
            return "I'm sorry, I had a problem uploading the video."

    def _execute_dubbing_plan(self, plan_str: str) -> str:
        """Executes the plan to dub the last video into another language."""
        print("🌐 Persona is executing a dubbing plan...")
        if not self.last_video_path or not self.last_video_commentary:
            return "I need to create a video with commentary first before I can dub it."

        match = re.search(r"lang\s+(\w+)", plan_str, re.IGNORECASE)
        if not match:
            return "I need to know which language to dub the video in."

        target_lang = match.group(1)

        # 1. Translate commentary
        translated_commentary = self.translator.translate(self.last_video_commentary, target_lang)

        # 2. Synthesize new audio
        # TODO: This requires having different voice prompts for different languages.
        # For now, we'll reuse the same voice but speak a different language.
        dub_audio_path = f"temp_dub_{target_lang}.wav"
        self.tts_manager.speak(
            translated_commentary,
            f"voices/{self.__class__.__name__.lower()}.wav", # Placeholder for language-specific voice
            output_path=dub_audio_path,
            language=target_lang
        )

        # 3. Replace audio in the original video
        dubbed_video_path = f"dubbed_{target_lang}_{Path(self.last_video_path).name}"
        self.video_editor.replace_audio(self.last_video_path, dub_audio_path, dubbed_video_path)

        # 4. Cleanup
        Path(dub_audio_path).unlink(missing_ok=True)

        self.last_video_path = dubbed_video_path # The new dubbed video is now the "last video"

        return f"I've dubbed the video in {target_lang}! It's ready at '{dubbed_video_path}'."

    def _execute_episode_creation_plan(self, plan_str: str) -> str:
        """Orchestrates the entire animation episode creation workflow."""
        print("🎞️ Persona is executing an episode creation plan...")

        match = re.search(r"prompt\s+([^,\]]+)", plan_str, re.IGNORECASE)
        if not match:
            return "I need a prompt to create an episode."

        story_prompt = match.group(1).strip()

        # 1. Write the script
        script_text = self.brain.write_episode_script(story_prompt)

        # 2. Parse the script into a storyboard
        scenes = self.storyboarder.parse_script(script_text)
        if not scenes:
            return "I had trouble creating a storyboard from the script."

        # 3. Generate assets and animate each scene
        scene_clips = []
        for i, scene in enumerate(scenes):
            print(f"--- Processing Scene {i+1} ---")
            scene_image_path = self.image_generator.generate_image(
                scene['description'],
                output_path=f"temp_scene_{i+1}.png"
            )
            if not scene_image_path: continue

            # Create animated clips for each character's dialogue
            for char, dialogue in scene['dialogue'].items():
                dialogue_audio_path = f"temp_dialogue_{i+1}_{char}.wav"
                self.tts_manager.speak(
                    dialogue,
                    f"voices/{char.lower()}.wav",
                    output_path=dialogue_audio_path
                )

                # For now, we assume we have static images for each character
                # In a real implementation, we'd have character models
                char_image_path = f"characters/{char.lower()}.png"
                if not Path(char_image_path).exists():
                    # Fallback to the scene image if a character image is missing
                    char_image_path = scene_image_path

                animated_clip_path = self.animator.animate_lip_sync(
                    char_image_path,
                    dialogue_audio_path,
                    output_path=f"temp_clip_{i+1}_{char}.mp4"
                )
                if animated_clip_path:
                    scene_clips.append(animated_clip_path)

        # 4. Stitch all animated clips together
        if not scene_clips:
            return "I couldn't create any animated clips for the episode."

        final_episode_path = f"episode_{story_prompt.replace(' ', '_')[:20]}.mp4"
        self.video_editor.stitch_videos(scene_clips, final_episode_path)

        # 5. Cleanup temporary files
        for path in Path('.').glob('temp_*'):
            path.unlink()

        self.last_video_path = final_episode_path
        return f"I've finished the new episode! It's ready at '{final_episode_path}'."