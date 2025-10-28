from googlesearch import search
from maya_ai.skills.skill import Skill

class WebSearchSkill(Skill):
    def get_name(self) -> str:
        return "Web Search Skill"

    def get_possible_actions(self) -> list:
        return [
            {
                "name": "search_web",
                "description": "Searches the web for a given query.",
                "args": {"query": "string"}
            }
        ]

    def perform_action(self, action_name: str, **kwargs) -> str:
        if action_name == "search_web":
            query = kwargs.get("query")
            if not query:
                return "Error: query is required."
            return self._search_web(query)
        return f"Unknown action: {action_name}"

    def _search_web(self, query: str) -> str:
        try:
            results = search(query, num_results=5)
            return "\n".join(results)
        except Exception as e:
            return f"Error performing web search: {e}"

def create_skill(config_manager):
    return WebSearchSkill()
