from maya_ai.skills.skill import Skill
from supertools import llm_google_search

class SearchSkill(Skill):
    """
    A skill that allows Maya to search the web.
    """
    def get_name(self) -> str:
        return "web_search"

    def get_possible_actions(self) -> list:
        return [
            {
                "name": "search",
                "description": "Searches the web for information on a given topic.",
                "params": {"query": "The search query."}
            }
        ]

    def perform_action(self, action_name: str, **kwargs) -> str:
        if action_name == "search":
            query = kwargs.get("query")
            if not query:
                return "Error: No search query provided."

            try:
                # Use the built-in google_search tool
                search_results = llm_google_search(query=query)
                # Format the results into a readable string for the LLM
                formatted_results = "\n".join([f"- {r['title']}: {r['snippet']}" for r in search_results['results']])
                return f"Here are the top search results for '{query}':\n{formatted_results}"
            except Exception as e:
                return f"An error occurred during the web search: {e}"

        return f"Error: Action '{action_name}' not found in {self.get_name()}."

def create_skill() -> Skill:
    """
    Factory function to create the SearchSkill instance.
    """
    return SearchSkill()
