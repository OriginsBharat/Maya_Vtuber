import pytchat
import threading
import time
from loguru import logger

class YouTubeChatListener:
    """
    Listens to a YouTube livestream chat and collects messages.
    """
    def __init__(self, video_id: str):
        """
        Initializes the chat listener.

        Args:
            video_id: The ID of the YouTube video to listen to.
        """
        self.video_id = video_id
        self.chat = pytchat.create(video_id=self.video_id)
        self.messages = []
        self._is_running = False
        self._thread = None

    def _run(self):
        """
        The main loop for the chat listener thread.
        """
        while self._is_running and self.chat.is_alive():
            for c in self.chat.get().items:
                message = f"{c.author.name}: {c.message}"
                self.messages.append(message)
            time.sleep(1)

    def start(self):
        """
        Starts the chat listener in a new thread.
        """
        if not self._is_running:
            self._is_running = True
            self._thread = threading.Thread(target=self._run)
            self._thread.daemon = True
            self._thread.start()
            logger.info(f"Started listening to chat for video ID: {self.video_id}")

    def stop(self):
        """
        Stops the chat listener.
        """
        self._is_running = False
        if self._thread:
            self._thread.join()
        logger.info("Stopped listening to chat.")

    def get_messages(self) -> list:
        """
        Gets the latest batch of messages and clears the internal list.

        Returns:
            A list of new chat messages.
        """
        # Return a copy and clear the list
        new_messages = list(self.messages)
        self.messages = []
        return new_messages

# Example usage (for testing)
if __name__ == '__main__':
    # You need a live YouTube video ID to test this.
    # Replace 'YOUR_VIDEO_ID' with a real, currently live video ID.
    VIDEO_ID = "YOUR_VIDEO_ID"

    listener = YouTubeChatListener(video_id=VIDEO_ID)
    listener.start()

    try:
        for _ in range(3): # Run for 30 seconds
            time.sleep(10)
            messages = listener.get_messages()
            if messages:
                print("\n--- New Messages ---")
                for msg in messages:
                    print(msg)
            else:
                print("\n--- No new messages ---")
    finally:
        listener.stop()
