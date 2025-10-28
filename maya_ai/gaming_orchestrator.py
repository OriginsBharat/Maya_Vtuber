import time
import json
from maya_ai.brain.core import Brain
from maya_ai.skills.skill_manager import SkillManager

class GamingOrchestrator:
    def __init__(self, brain: Brain, skill_manager: SkillManager):
        self.brain = brain
        self.skill_manager = skill_manager
        self.minecraft_skill = self.skill_manager.get_skill("Minecraft Skill")
        self.is_running = False

    def start_autonomous_loop(self, goal: str):
        if not self.minecraft_skill:
            print("Minecraft skill not found.")
            return

        self.is_running = True
        print(f"Starting autonomous gaming loop with goal: {goal}")

        while self.is_running:
            try:
                world_state = self.minecraft_skill.perform_action("get_world_state")
                action_json = self.brain.get_gaming_action(world_state, goal)
                action = json.loads(action_json)
                self.minecraft_skill.perform_action("game_action", action=action)
                time.sleep(5)
            except KeyboardInterrupt:
                self.stop_autonomous_loop()
            except Exception as e:
                print(f"An error occurred in the autonomous loop: {e}")
                self.stop_autonomous_loop()

    def stop_autonomous_loop(self):
        self.is_running = False
        print("Stopping autonomous gaming loop.")
