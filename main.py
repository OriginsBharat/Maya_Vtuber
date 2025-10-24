from maya_ai.persona import Persona
import os
import sys

def load_prompt(file_path: str) -> str:
    """Loads a prompt from a text file."""
    if not os.path.exists(file_path):
        print(f"Error: Prompt file not found at: {file_path}", file=sys.stderr)
        sys.exit(1)
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    """
    Main function to run the Maya VTuber console application.
    """
    print("Initializing Maya VTuber...")

    try:
        # Define paths for the persona prompts
        sarjana_prompt_path = "maya_ai/prompts/sarjana.txt"
        durjana_prompt_path = "maya_ai/prompts/durjana.txt"

        # Load the prompts from the files
        sarjana_prompt = load_prompt(sarjana_prompt_path)
        durjana_prompt = load_prompt(durjana_prompt_path)

        # Create the persona agents
        sarjana = Persona(name="Sarjana", system_prompt=sarjana_prompt)
        durjana = Persona(name="Durjana", system_prompt=durjana_prompt)

        print("Sarjana and Durjana are ready. Type 'quit' to exit.")
        print("-" * 30)

        while True:
            # Get user input for the meme description
            meme_description = input("Enter a meme description: ")

            if meme_description.lower() == 'quit':
                break

            # --- Conversation Loop ---
            print("-" * 30)
            print(f"Reacting to: {meme_description}")
            print("-" * 30)

            # 1. Sarjana reacts to the meme
            sarjana_context = f"You see a meme described as: '{meme_description}'. What is your first reaction?"
            sarjana_response = sarjana.generate_response(sarjana_context)
            print(f"Sarjana: {sarjana_response}")

            # 2. Durjana reacts to Sarjana's comment and the meme
            durjana_context = f"You see a meme described as: '{meme_description}'. Your sister, Sarjana, just said: '{sarjana_response}'. How do you respond to her and the meme?"
            durjana_response = durjana.generate_response(durjana_context)
            print(f"Durjana: {durjana_response}")

            # Reset history for the next meme to avoid context bleed
            sarjana.reset_history()
            durjana.reset_history()

            print("-" * 30)

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
