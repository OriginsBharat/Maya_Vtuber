import asyncio
import pyvts
from loguru import logger

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
            logger.info("Successfully connected to VTube Studio.")
        except Exception as e:
            logger.error(f"Failed to connect to VTube Studio: {e}", exc_info=True)
            self.is_connected = False

    async def disconnect(self):
        """
        Disconnects from the VTube Studio API.
        """
        if self.is_connected:
            await self.vts.close()
            self.is_connected = False
            logger.info("Disconnected from VTube Studio.")

    async def trigger_hotkey(self, hotkey_name: str):
        """
        Triggers a specific hotkey in VTube Studio.

        Args:
            hotkey_name: The name of the hotkey to trigger.
        """
        if not self.is_connected:
            logger.warning("Not connected to VTube Studio.")
            return

        hotkey_request = self.vts.vts_request.requestTriggerHotKey(hotkey_name)
        try:
            await self.vts.request(hotkey_request)
            logger.info(f"Triggered hotkey: {hotkey_name}")
        except Exception as e:
            logger.error(f"Failed to trigger hotkey {hotkey_name}: {e}", exc_info=True)

async def main():
    logger.add("logs/maya.log", level="INFO", rotation="10 MB", retention="5 days")
    vts_manager = VTSManager()
    await vts_manager.connect()

    if vts_manager.is_connected:
        logger.info("\n--- Testing Hotkey Triggers ---")
        logger.info("Triggering 'StartTalking' (imagine avatar mouth opens)...")
        await vts_manager.trigger_hotkey("StartTalking")

        await asyncio.sleep(3)

        logger.info("Triggering 'StopTalking' (imagine avatar mouth closes)...")
        await vts_manager.trigger_hotkey("StopTalking")

        await vts_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
