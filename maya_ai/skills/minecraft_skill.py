from maya_ai.skills.skill import Skill
import websocket
import json

import subprocess

class MinecraftSkill(Skill):
    def __init__(self):
        self.ws = None
        self.bot_process = None

    def get_name(self) -> str:
        return "Minecraft Skill"

    def get_possible_actions(self) -> list:
        return [
            {"name": "start_bot", "description": "Starts the Minecraft bot."},
            {"name": "stop_bot", "description": "Stops the Minecraft bot."},
            {"name": "connect", "description": "Connects to the Minecraft bot.", "args": {"uri": "string"}},
            {"name": "disconnect", "description": "Disconnects from the Minecraft bot."},
            {"name": "game_action", "description": "Sends a game action to the Minecraft bot.", "args": {"action": "dict"}},
            {"name": "get_world_state", "description": "Gets the world state from the Minecraft bot."},
        ]

    def perform_action(self, action_name: str, **kwargs) -> str:
        if action_name == "start_bot":
            return self._start_bot()
        elif action_name == "stop_bot":
            return self._stop_bot()
        elif action_name == "connect":
            return self._connect(**kwargs)
        elif action_name == "disconnect":
            return self._disconnect()
        elif action_name == "game_action":
            return self._send_command("game_action", kwargs.get("action"))
        elif action_name == "get_world_state":
            return self._get_world_state()
        return f"Unknown action: {action_name}"

    def _start_bot(self):
        if self.bot_process:
            return "Bot is already running."
        try:
            self.bot_process = subprocess.Popen(
                ["node", "bot.js"], cwd="minecraft_bot", stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            return "Minecraft bot started."
        except FileNotFoundError:
            return "Node.js not found."
        except Exception as e:
            return f"Failed to start Minecraft bot: {e}"

    def _stop_bot(self):
        if self.bot_process:
            self.bot_process.kill()
            self.bot_process = None
            return "Minecraft bot stopped."
        return "Bot is not running."

    def _connect(self, uri="ws://localhost:3000"):
        try:
            self.ws = websocket.create_connection(uri)
            return "Connected to Minecraft bot."
        except Exception as e:
            return f"Failed to connect to Minecraft bot: {e}"

    def _disconnect(self):
        if self.ws:
            self.ws.close()
            return "Disconnected from Minecraft bot."
        return "Not connected."

    def _send_command(self, command: str, args: dict = None):
        if not self.ws:
            return "Not connected to Minecraft bot."
        payload = {"command": command, "args": args or {}}
        self.ws.send(json.dumps(payload))
        result = self.ws.recv()
        return json.loads(result).get("status", "error")

    def _get_world_state(self):
        if not self.ws:
            return "Not connected to Minecraft bot."
        payload = {"command": "get_world_state"}
        self.ws.send(json.dumps(payload))
        result = self.ws.recv()
        return json.loads(result)

def create_skill(config_manager):
    return MinecraftSkill()
