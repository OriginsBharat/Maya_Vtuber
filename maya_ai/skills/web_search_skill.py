from googlesearch import search
from maya_ai.skills.skill import Skill
from loguru import logger

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
                logger.error("query is required for search_web action.")
                return "Error: query is required."
            return self._search_web(query)
        logger.warning(f"Unknown action for Web Search Skill: {action_name}")
        return f"Unknown action: {action_name}"

    def _search_web(self, query: str) -> str:
        try:
            logger.info(f"Searching web for: '{query}'")
            results = search(query, num_results=5)
            logger.info("Web search successful.")
            return "\n".join(results)
        except Exception as e:
            logger.error(f"Error performing web search: {e}", exc_info=True)
            return f"Error performing web search: {e}"

def create_skill(brain):
    return WebSearchSkill()
