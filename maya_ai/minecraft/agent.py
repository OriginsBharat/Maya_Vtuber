import websocket
import threading
import json
import time

class MinecraftAgent:
    """
    The Python client that connects to the Mineflayer bot via WebSocket.
    """
    def __init__(self):
        self.ws = None
        self.thread = None
        self.latest_world_state = {}
        self.is_connected = False
        self.ws_url = None
        self.host = None
        self.port = None
        self.username = None

    def connect(self, host="localhost", port=3000, username="Maya"):
        """Connects to the WebSocket server."""
        self.host = host
        self.port = port
        self.username = username
        self.ws_url = f"ws://localhost:{port}"
        print("🐍 Python agent attempting to connect to WebSocket bridge...")
        try:
            self.ws = websocket.WebSocketApp(self.ws_url,
                                             on_open=self.on_open,
                                             on_message=self.on_message,
                                             on_error=self.on_error,
                                             on_close=self.on_close)
            self.thread = threading.Thread(target=self.ws.run_forever)
            self.thread.daemon = True
            self.thread.start()

            # Wait for connection to be established
            timeout = 10
            while not self.is_connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1

            if not self.is_connected:
                print("🚨 Connection to WebSocket timed out.")
                return False

            return True
        except Exception as e:
            print(f"🚨 Failed to connect to WebSocket: {e}")
            return False

    def on_open(self, ws):
        print("✅ Python agent connected to WebSocket bridge.")
        self.is_connected = True
        connect_command = {
            "command": "connect",
            "args": {
                "host": self.host,
                "port": self.port,
                "username": self.username
            }
        }
        self.send_command(connect_command)

    def on_message(self, ws, message):
        """Handles incoming messages from the bot."""
        data = json.loads(message)
        if data.get('type') == 'world_state':
            self.latest_world_state = data
            # For debugging, we can print a summary
            # print(f"Received world state: Position {data['position']}")

    def on_error(self, ws, error):
        print(f"🚨 WebSocket Error: {error}")
        self.is_connected = False

    def on_close(self, ws, close_status_code, close_msg):
        print("🔴 WebSocket connection closed.")
        self.is_connected = False

    def send_command(self, command: dict):
        """Sends a command to the Mineflayer bot."""
        if self.is_connected:
            self.ws.send(json.dumps(command))
        else:
            print("🚨 Cannot send command: not connected to WebSocket.")

    def get_latest_world_state(self) -> dict:
        """Returns the most recent world state received from the bot."""
        return self.latest_world_state

    def disconnect(self):
        """Disconnects from the WebSocket server."""
        if self.ws:
            self.ws.close()