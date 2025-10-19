from maya_ai.brain.core import Brain
from maya_ai.memory.database import MemoryDatabase
from maya_ai.content.web_scraper import WebScraper
from maya_ai.tts.tts_manager import TTSManager
from maya_ai.video.editor import VideoEditor
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
        self.system_prompt = self._create_system_prompt()

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

        # Check if it's a multi-step plan
        if action_plan_str.startswith("[PLAN:"):
            return self._execute_video_creation_plan(action_plan_str)
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
        return final_message