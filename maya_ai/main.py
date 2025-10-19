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
from maya_ai.minecraft.agent import MinecraftAgent
import subprocess
import json

# --- Global Queues ---
public_chat_queue = queue.Queue()
director_voice_queue = queue.Queue()

def cli_mode(persona_instance):
    """Handles the command-line interface mode."""
    print(f"\n--- CLI Mode with {persona_instance.__class__.__name__} ---")
    print("(Type 'exit' to quit, 'switch' to change persona)")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit': return 'exit'
            if user_input.lower() == 'switch': return 'switch'
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
            text_queue.put('exit')
            break

def live_mode(persona_instance, tts_manager, youtube_listener):
    """Handles the live streaming mode."""
    print(f"\n--- Live Stream Mode with {persona_instance.__class__.__name__} ---")
    director_text_queue = queue.Queue()
    youtube_listener.start_polling(public_chat_queue)
    director_audio_listener = AudioListener(director_voice_queue)
    director_audio_listener.listen_continuously()
    director_text_thread = threading.Thread(target=_director_text_listener, args=(director_text_queue,), daemon=True)
    director_text_thread.start()
    print("Listening for YouTube Chat and Director's commands.")
    print("Enter your private text directives below. Type 'exit' to end.")
    while True:
        try:
            if not director_text_queue.empty():
                text = director_text_queue.get()
                if text.lower() == 'exit': return 'exit'
                if text.lower() == 'switch': return 'switch'
                final_message = persona_instance.execute_directive(text)
                tts_manager.speak(final_message, f"voices/{persona_instance.__class__.__name__.lower()}.wav")
                continue
            if not director_voice_queue.empty():
                voice_text = director_voice_queue.get()
                response = persona_instance.generate_response(voice_text, is_roleplay=True)
                tts_manager.speak(response, f"voices/{persona_instance.__class__.__name__.lower()}.wav")
            if not public_chat_queue.empty():
                chat_message = public_chat_queue.get()
                response = persona_instance.generate_response(chat_message)
                tts_manager.speak(response, f"voices/{persona_instance.__class__.__name__.lower()}.wav")
            time.sleep(0.1)
        except (KeyboardInterrupt, EOFError):
            return 'exit'

def gaming_mode(brain):
    """Handles the Mineflayer-based gaming mode."""
    print("\n--- Gaming Mode ---")

    # 1. Launch the Node.js Mineflayer bot as a background process
    print("🚀 Launching Mineflayer bot...")
    bot_process = subprocess.Popen(["node", "mineflayer_bot/index.js"])

    # 2. Connect our Python agent to the bot via WebSocket
    agent = MinecraftAgent()
    if not agent.connect():
        print("🚨 Could not connect to Mineflayer bot. Aborting Gaming Mode.")
        bot_process.terminate() # Clean up the bot process
        return

    print("✅ Agent connected. Starting the see-think-act loop.")
    print("Press Ctrl+C to exit.")

    # 3. Start the see -> think -> act loop
    goal = "gather 5 oak logs" # Initial goal
    while True:
        try:
            # Sense: Get the latest world state from the agent
            world_state = agent.get_latest_world_state()
            if not world_state:
                time.sleep(1)
                continue

            # Think: Ask the brain for the next action based on the state and goal
            action_json_str = brain.get_gaming_action(world_state, goal)

            # Act: Send the command to the bot
            try:
                action_command = json.loads(action_json_str)
                agent.send_command(action_command)
            except json.JSONDecodeError:
                print(f"🚨 Brain returned invalid action JSON: {action_json_str}")

            # Wait a moment before the next cycle
            time.sleep(5) # Give the bot time to perform the action

        except KeyboardInterrupt:
            print("\nExiting Gaming Mode...")
            agent.disconnect()
            bot_process.terminate()
            return 'exit'

def main():
    """Main entry point for the application."""
    print("🧠 Maya AI Initializing...")
    try:
        brain = Brain()
        db_path = Path.home() / ".maya_ai" / "memory.db"
        memory = MemoryDatabase(db_path=db_path)
        print("✅ Core modules initialized.")
    except Exception as e:
        print(f"🚨 FATAL ERROR during initialization: {e}")
        return

    username = "originsbharat"
    user_id = memory.get_or_create_user(username)
    print(f"Welcome, {username} (User ID: {user_id})")

    tts_manager = None
    active_persona_instance = None

    while True:
        print("\nSelect Mode:")
        print("1. CLI Mode")
        print("2. Live Stream Mode")
        print("3. Gaming Mode")
        print("4. Exit")
        mode_choice = input("> ")

        if mode_choice == '1' or mode_choice == '2':
            if active_persona_instance is None:
                print("\nPlease select a persona first:")
                print("1: Sarjana (The Good Daughter)")
                print("2: Durjana (The Bratty Daughter)")
                persona_choice = input("> ")
                if not tts_manager:
                    try:
                        tts_manager = TTSManager(cfg_path="checkpoints/config.yaml", model_dir="checkpoints")
                    except Exception as e:
                        print(f"🚨 TTS Warning: {e}\n🚨 TTS will be disabled for this session.")
                if persona_choice == '1':
                    active_persona_instance = Sarjana(brain, memory, user_id, tts_manager)
                elif persona_choice == '2':
                    active_persona_instance = Durjana(brain, memory, user_id, tts_manager)
                else:
                    print("Invalid persona choice.")
                    continue

            if mode_choice == '1':
                result = cli_mode(active_persona_instance)
            else: # mode_choice == '2'
                if not tts_manager:
                    print("🚨 Live Stream Mode requires TTS. Please resolve TTS issues.")
                    continue
                try:
                    youtube_listener = YouTubeListener(video_id="YOUR_VIDEO_ID_HERE")
                    result = live_mode(active_persona_instance, tts_manager, youtube_listener)
                except Exception as e:
                    print(f"🚨 Live Stream ERROR: {e}")
                    continue

            if result == 'switch':
                active_persona_instance = None
                continue

        elif mode_choice == '3':
            gaming_mode(brain)

        elif mode_choice == '4':
            break
        else:
            print("Invalid mode.")
            continue

    memory.close()
    print("\n👋 Maya AI Shutting Down. Goodbye!")

if __name__ == "__main__":
    main()