from pathlib import Path
from maya_ai.brain.core import Brain
from maya_ai.memory.database import MemoryDatabase
from maya_ai.personas.sarjana import Sarjana
from maya_ai.personas.durjana import Durjana

def main():
    """
    The main entry point for the Maya AI command-line interface.
    """
    print("🧠 Maya AI Initializing...")

    # --- Initialization ---
    try:
        brain = Brain()
        db_path = Path.home() / ".maya_ai" / "memory.db"
        memory = MemoryDatabase(db_path=db_path)
        print("✅ Brain and Memory loaded.")
    except ValueError as e:
        print(f"🚨 FATAL ERROR: {e}")
        print("🚨 Please create a .env file in the 'maya_ai' directory with your ANTHROPIC_API_KEY.")
        return

    # --- User Setup ---
    # For this first milestone, we'll hardcode the user as 'originsbharat'
    username = "originsbharat"
    user_id = memory.get_or_create_user(username)
    print(f"Welcome, {username}! (User ID: {user_id})")

    # --- Main Loop ---
    active_persona_instance = None
    while True:
        if active_persona_instance is None:
            # --- Persona Selection ---
            print("\nWho do you want to talk to?")
            print("1: Sarjana (The Good Daughter)")
            print("2: Durjana (The Bratty Daughter)")
            print("exit: Close the application")
            choice = input("> ")

            if choice == '1':
                active_persona_instance = Sarjana(brain, memory, user_id)
                print("\n🌸 You are now talking to Sarjana. (Type 'switch' to change persona)")
            elif choice == '2':
                active_persona_instance = Durjana(brain, memory, user_id)
                print("\n🔥 You are now talking to Durjana. (Type 'switch' to change persona)")
            elif choice.lower() == 'exit':
                break
            else:
                print("Invalid choice. Please try again.")
                continue

        # --- Chatting Loop ---
        try:
            user_input = input("You: ")
            if user_input.lower() == 'switch':
                active_persona_instance = None
                continue
            if user_input.lower() == 'exit':
                break

            response = active_persona_instance.generate_response(user_input)

            persona_name = active_persona_instance.__class__.__name__
            print(f"{persona_name}: {response}")

        except KeyboardInterrupt:
            # Allow exiting with Ctrl+C
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    # --- Shutdown ---
    memory.close()
    print("\n👋 Maya AI Shutting Down. Goodbye!")

if __name__ == "__main__":
    main()