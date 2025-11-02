import threading
import time
from loguru import logger
from maya_ai.config.config_loader import get_config
from maya_ai.skills.skill_manager import SkillManager

from maya_ai.brain.brain import Brain
from maya_ai.personas.persona import Persona

class ProactiveOrchestrator:
    """
    Manages the autonomous, proactive content discovery and suggestion loop.
    """
    def __init__(self, brain: Brain, skill_manager: SkillManager, personas: dict[str, Persona]):
        """
        Initializes the Proactive Orchestrator.

        Args:
            brain: The AI Brain to use for analysis.
            skill_manager: An instance of SkillManager to access skills like RedditScraper.
            personas: A dictionary of loaded Persona objects.
        """
        self.config = get_config()
        self.brain = brain
        self.skill_manager = skill_manager
        self.personas = personas
        self.suggestions = []  # This will hold the generated suggestions
        self.is_running = False
        self._thread = None

        self.shared_subreddits = self.config.get('proactive_creator', 'shared_subreddits', [])
        logger.info(f"Proactive Orchestrator initialized. Will scan subreddits: {self.shared_subreddits}")

    def _discovery_loop(self):
        """
        The main background loop for content discovery.
        """
        logger.info("Starting proactive content discovery loop...")
        while self.is_running:
            logger.info("Scanning for new content...")

            scan_interval = self.config.get('proactive_creator', 'scan_interval_seconds', 3600)
            reddit_scraper = self.skill_manager.get_skill("Reddit Scraper Skill")
            if not reddit_scraper:
                logger.error("Reddit Scraper Skill not found. Cannot perform content discovery.")
                time.sleep(scan_interval)
                continue

            # In a real-world scenario, we'd track seen posts to avoid duplicates.
            # For this implementation, we just fetch top posts each time.
            all_posts = []
            for subreddit in self.shared_subreddits:
                posts = reddit_scraper.perform_action("get_top_posts", subreddit_name=subreddit, limit=10)
                # The skill returns a list of titles, but we need more info.
                # This is a limitation we'll accept for now. We'll simulate having a URL.
                for post_title in posts:
                    if "Error:" not in post_title:
                        all_posts.append({
                            "title": post_title,
                            "url": f"https://www.reddit.com/r/{subreddit}/" # Simulated URL
                        })

            logger.info(f"Fetched {len(all_posts)} posts to analyze.")

            for post in all_posts:
                for persona_name, persona in self.personas.items():
                    prompt = self._create_analysis_prompt(post['title'], persona.get_description())

                    response_text = self.brain.think(prompt)

                    if response_text.strip().upper().startswith("YES"):
                        take = response_text.strip()[3:].strip() # Get the text after "YES"
                        suggestion = {
                            "persona_name": persona_name,
                            "title": post['title'],
                            "url": post['url'],
                            "take": take,
                            "status": "pending"
                        }
                        self.suggestions.append(suggestion)
                        logger.success(f"New suggestion from {persona_name}: {post['title']}")

            # Wait for a configured interval before the next scan
            scan_interval = self.config.get('proactive_creator', 'scan_interval_seconds', 3600)
            logger.info(f"Scan complete. Waiting {scan_interval} seconds for the next scan.")
            time.sleep(scan_interval)

        logger.info("Proactive content discovery loop stopped.")

    def _create_analysis_prompt(self, post_title: str, persona_description: str) -> str:
        """
        Creates the prompt for the LLM to analyze a post title.
        """
        return f"""
You are an AI persona with the following personality: {persona_description}

You are browsing Reddit for content ideas. Analyze the following post title:
"{post_title}"

Based on your personality, is this post interesting enough for you to comment on or create content about?
Your answer MUST start with "YES" or "NO".
If YES, follow it with a short, in-character "take" or "angle" on why it's interesting to you.
If NO, simply state "NO".

Example YES response:
YES. This is hilarious, it reminds me of the time...

Example NO response:
NO.

Your response:
"""

    def start(self):
        """
        Starts the content discovery loop in a background thread.
        """
        if not self.is_running:
            self.is_running = True
            self._thread = threading.Thread(target=self._discovery_loop, daemon=True)
            self._thread.start()
            logger.info("Proactive Orchestrator has been started.")

    def stop(self):
        """
        Stops the content discovery loop.
        """
        if self.is_running:
            self.is_running = False
            if self._thread:
                # The loop will naturally exit on its next iteration.
                # If immediate shutdown is needed, a more complex mechanism like an Event would be used.
                logger.info("Proactive Orchestrator is stopping.")

    def get_suggestions(self):
        """
        Returns the list of generated content suggestions.
        """
        return self.suggestions
