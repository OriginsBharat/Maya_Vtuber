from javascript import require, On, once
from maya_ai.skills.skill import Skill

mineflayer = require('mineflayer')

class MinecraftSkill(Skill):
    def __init__(self):
        self.bot = None

    def get_name(self) -> str:
        return "Minecraft Skill"

    def get_possible_actions(self) -> list:
        return [
            {"name": "connect", "description": "Connects to a Minecraft server.", "args": {"host": "string", "port": "int", "username": "string"}},
            {"name": "disconnect", "description": "Disconnects from the Minecraft server."},
            {"name": "get_world_state", "description": "Gets the world state from the bot."},
            {"name": "game_action", "description": "Sends a game action to the Minecraft bot.", "args": {"action": "dict"}},
        ]

    def perform_action(self, action_name: str, **kwargs) -> str:
        if action_name == "connect":
            return self._connect(**kwargs)
        elif action_name == "disconnect":
            return self._disconnect()
        elif action_name == "get_world_state":
            return self._get_world_state()
        elif action_name == "game_action":
            return self._game_action(**kwargs)
        return f"Unknown action: {action_name}"

    def _connect(self, host, port, username):
        try:
            self.bot = mineflayer.createBot({
                'host': host,
                'port': port,
                'username': username
            })
            return "Connected to Minecraft server."
        except Exception as e:
            return f"Failed to connect to Minecraft server: {e}"

    def _disconnect(self):
        if self.bot:
            self.bot.quit()
            self.bot = None
            return "Disconnected from Minecraft server."
        return "Not connected."

    def _get_world_state(self):
        if not self.bot:
            return "Not connected."

        inventory = self.bot.inventory.items()
        return {
            "inventory": [{"name": item.name, "count": item.count} for item in inventory],
            "position": self.bot.entity.position
        }

    def _game_action(self, action):
        if not self.bot:
            return "Not connected."

        command = action.get("command")
        args = action.get("args", [])

        if hasattr(self.bot, command):
            getattr(self.bot, command)(*args)
            return f"Executed command: {command}"
        return f"Unknown command: {command}"

def create_skill(config_manager):
    return MinecraftSkill()
