import asyncio
import pyvts

class VTSManager:
    """
    Manages the connection and interaction with the VTube Studio API.
    """
    def __init__(self):
        """
        Initializes the VTSManager.
        """
        self.vts = pyvts.vts()
        self.is_connected = False
        self.plugin_info = {
            "plugin_name": "MayaAI",
            "developer": "originsbharat",
            "authentication_token_path": "./token.txt"
        }

    async def connect(self):
        """
        Connects to the VTube Studio API.
        """
        if self.is_connected:
            return

        try:
            await self.vts.connect()
            await self.vts.request_authenticate_token()
            await self.vts.request_authenticate()
            self.is_connected = True
            print("Successfully connected to VTube Studio.")
        except Exception as e:
            print(f"Failed to connect to VTube Studio: {e}")
            self.is_connected = False

    async def disconnect(self):
        """
        Disconnects from the VTube Studio API.
        """
        if self.is_connected:
            await self.vts.close()
            self.is_connected = False
            print("Disconnected from VTube Studio.")

    async def trigger_hotkey(self, hotkey_name: str):
        """
        Triggers a specific hotkey in VTube Studio.

        Args:
            hotkey_name: The name of the hotkey to trigger.
        """
        if not self.is_connected:
            print("Not connected to VTube Studio.")
            return

        hotkey_request = self.vts.vts_request.requestTriggerHotKey(hotkey_name)
        try:
            await self.vts.request(hotkey_request)
            print(f"Triggered hotkey: {hotkey_name}")
        except Exception as e:
            print(f"Failed to trigger hotkey {hotkey_name}: {e}")

# Example usage for testing
async def main():
    vts_manager = VTSManager()
    await vts_manager.connect()

    if vts_manager.is_connected:
        # In a real scenario, you would have hotkeys in VTube Studio
        # named "StartTalking" and "StopTalking" that control the mouth open parameter.
        print("\n--- Testing Hotkey Triggers ---")
        print("Triggering 'StartTalking' (imagine avatar mouth opens)...")
        await vts_manager.trigger_hotkey("StartTalking")

        await asyncio.sleep(3) # Simulate talking for 3 seconds

        print("Triggering 'StopTalking' (imagine avatar mouth closes)...")
        await vts_manager.trigger_hotkey("StopTalking")

        await vts_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
