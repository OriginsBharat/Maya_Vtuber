import queue
import threading
import time
from pathlib import Path

from maya_ai.brain.core import Brain
from maya_ai.memory.database import MemoryDatabase
from maya_ai.personas.sarjana import Sarjana
from maya_ai.personas.durjana import Durjana
from maya_ai.tts.tts_manager import TTSManager
from maya_ai.livestream.youtube_listener import YouTubeListener
from maya_ai.director.audio_listener import AudioListener

# --- Global Queues ---
# A queue for messages from the public (YouTube chat)
public_chat_queue = queue.Queue()
# A queue for private voice messages from the director
director_voice_queue = queue.Queue()

def cli_mode(persona_instance):
    """Handles the command-line interface mode."""
    print(f"Entering CLI Mode with {persona_instance.__class__.__name__}.")
    print("(Type 'exit' to quit, 'switch' to change persona)")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                return 'exit'
            if user_input.lower() == 'switch':
                return 'switch'

            response = persona_instance.generate_response(user_input)
            print(f"{persona_instance.__class__.__name__}: {response}")
        except (KeyboardInterrupt, EOFError):
            return 'exit'

def _director_text_listener(text_queue: queue.Queue):
    """Worker thread to listen for director's text input without blocking."""
    while True:
        try:
            text = input()
            text_queue.put(text)
        except EOFError:
            # This allows the program to exit cleanly
            text_queue.put('exit')
            break

def live_mode(persona_instance, tts_manager, youtube_listener):
    """Handles the live streaming mode."""
    print(f"Entering Live Mode with {persona_instance.__class__.__name__}.")

    # Create a queue for the director's text input
    director_text_queue = queue.Queue()

    # Start all background listeners
    youtube_listener.start_polling(public_chat_queue)

    director_audio_listener = AudioListener(director_voice_queue)
    director_audio_listener.listen_continuously()

    director_text_thread = threading.Thread(target=_director_text_listener, args=(director_text_queue,), daemon=True)
    director_text_thread.start()

    print("\n--- Live Stream is Active ---")
    print("Listening to YouTube Chat and Director's commands.")
    print("Enter your private text directives in the console and press Enter.")
    print("Type 'exit' to end stream, 'switch' to change persona.")

    while True:
        try:
            # Process queues in order of priority

            # 1. Check for Director's Text Directives
            if not director_text_queue.empty():
                text = director_text_queue.get()
                if text.lower() == 'exit': return 'exit'
                if text.lower() == 'switch': return 'switch'
                response = persona_instance.execute_directive(text)
                tts_manager.speak(response, f"voices/{persona_instance.__class__.__name__.lower()}.wav")
                continue

            # 2. Check for Director's Voice Input
            if not director_voice_queue.empty():
                voice_text = director_voice_queue.get()
                response = persona_instance.generate_response(voice_text, is_roleplay=True)
                tts_manager.speak(response, f"voices/{persona_instance.__class__.__name__.lower()}.wav")

            # 3. Check for Public YouTube Chat
            if not public_chat_queue.empty():
                chat_message = public_chat_queue.get()
                response = persona_instance.generate_response(chat_message)
                tts_manager.speak(response, f"voices/{persona_instance.__class__.__name__.lower()}.wav")

            # Prevent busy-waiting
            time.sleep(0.1)

        except (KeyboardInterrupt, EOFError):
            return 'exit'

def main():
    """Main entry point for the application."""
    print("🧠 Maya AI Initializing...")

    try:
        brain = Brain()
        db_path = Path.home() / ".maya_ai" / "memory.db"
        memory = MemoryDatabase(db_path=db_path)

        # TODO: Make these paths configurable
        tts_manager = TTSManager(
            cfg_path="checkpoints/config.yaml",
            model_dir="checkpoints"
        )

        # TODO: Get video ID from user input
        youtube_listener = YouTubeListener(video_id="YOUR_VIDEO_ID_HERE")

        print("✅ Core modules initialized.")
    except Exception as e:
        print(f"🚨 FATAL ERROR during initialization: {e}")
        print("🚨 Please ensure all required models and credentials are in place.")
        return

    username = "originsbharat"
    user_id = memory.get_or_create_user(username)
    print(f"Welcome, {username} (User ID: {user_id})")

    active_persona_instance = None
    while True:
        if active_persona_instance is None:
            print("\nWho do you want to use?")
            print("1: Sarjana (The Good Daughter)")
            print("2: Durjana (The Bratty Daughter)")
            choice = input("> ")
            if choice == '1':
                active_persona_instance = Sarjana(brain, memory, user_id)
            elif choice == '2':
                active_persona_instance = Durjana(brain, memory, user_id)
            else:
                print("Invalid choice.")
                continue

        print("\nSelect Mode:")
        print("1. CLI Mode")
        print("2. Live Stream Mode")
        mode_choice = input("> ")

        result = None
        if mode_choice == '1':
            result = cli_mode(active_persona_instance)
        elif mode_choice == '2':
            result = live_mode(active_persona_instance, tts_manager, youtube_listener)
        else:
            print("Invalid mode.")
            continue

        if result == 'exit':
            break
        if result == 'switch':
            active_persona_instance = None
            continue

    memory.close()
    print("\n👋 Maya AI Shutting Down. Goodbye!")

if __name__ == "__main__":
    main()