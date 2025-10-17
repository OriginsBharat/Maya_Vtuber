import os
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Brain:
    """
    The core brain of Maya. It handles the fundamental interaction with the LLM.
    It is designed to be model-agnostic, so the underlying client can be swapped.
    """
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file.")

        # For now, we are using Anthropic's client. This can be replaced with any other client.
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def get_response(self, system_prompt: str, conversation_history: list, latest_message: str) -> str:
        """
        Gets a standard conversational response from the language model.

        Args:
            system_prompt: The persona definition for the AI.
            conversation_history: A list of previous messages in the conversation.
            latest_message: The latest message from the user.

        Returns:
            The AI's response as a string.
        """
        messages = conversation_history + [{"role": "user", "content": latest_message}]
        return self._execute_llm_call(system_prompt, messages)

    def process_directive(self, directive: str, conversation_history: list) -> str:
        """
        Processes a high-level directive from the director.

        Args:
            directive: The natural language directive from the director.
            conversation_history: The recent chat history to provide context.

        Returns:
            A structured action plan for the persona to execute.
        """
        print(f"🧠 Brain processing directive: '{directive}'")

        # This meta-prompt instructs the LLM to act as a "Director's Assistant"
        # and translate a high-level goal into a concrete action.
        directive_system_prompt = """\
You are a logical processor for an AI VTuber. Your job is to translate a high-level directive from the director into a clear, actionable instruction for the AI persona.
The directive will be a natural language command. You must analyze it and the recent chat history to determine the best course of action.
Your output MUST be a short, clear, in-character instruction for the persona to follow.

Example Directive: "make fun of a creepy chatter"
Example Recent Chat:
- User1: Hi Maya!
- CreepyUser: you are so beautiful my angel i want to marry you
- User2: LOL

Your Action Plan Output: "Find the comment from 'CreepyUser' and roast them for being weird."

Example Directive: "thank our new subscriber"
Example Recent Chat:
- User3: Just subscribed! Love the stream!
- User4: Pog

Your Action Plan Output: "Thank 'User3' for subscribing and welcome them to the community."
"""

        # Format the message for the LLM
        directive_message = f"""\
Directive: "{directive}"

Recent Chat History:
{self._format_history_for_prompt(conversation_history)}

Your Action Plan Output:"""

        messages = [{"role": "user", "content": directive_message}]

        action_plan = self._execute_llm_call(directive_system_prompt, messages)
        print(f"💡 Brain generated action plan: '{action_plan}'")
        return action_plan

    def _format_history_for_prompt(self, conversation_history: list) -> str:
        """Helper to format history for the directive prompt."""
        return "\n".join([f"- {msg['role']}: {msg['content']}" for msg in conversation_history])

    def _execute_llm_call(self, system_prompt: str, messages: list) -> str:
        """A centralized method to call the LLM API."""
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
            return message.content[0].text
        except Exception as e:
            print(f"An error occurred while communicating with the AI model: {e}")
            return "I'm sorry, I'm having trouble thinking right now."