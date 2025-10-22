import os
import time
import queue
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class YouTubeListener:
    """
    Connects to YouTube Live Chat and fetches new messages.
    """
    SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

    def __init__(self, video_id: str, credentials_path: str = 'client_secrets.json'):
        """
        Initializes the YouTube listener.

        Args:
            video_id: The ID of the YouTube video with the live chat.
            credentials_path: Path to the Google Cloud client secrets file.
        """
        self.video_id = video_id
        self.credentials_path = credentials_path
        self.youtube = self._get_authenticated_service()
        self.live_chat_id = self._get_live_chat_id()
        self.last_request_time = None
        self.message_queue = queue.Queue()

    def _get_authenticated_service(self):
        """Authenticate and return a YouTube API service object."""
        creds = None
        # The file token.pickle stores the user's access and refresh tokens.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"'{self.credentials_path}' not found. Please download your "
                        "Google Cloud credentials and place them in the root directory."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return build('youtube', 'v3', credentials=creds)

    def _get_live_chat_id(self):
        """Get the live chat ID for the specified video."""
        request = self.youtube.videos().list(
            part="liveStreamingDetails",
            id=self.video_id
        )
        response = request.execute()

        if not response.get("items"):
            raise Exception("Video not found or no live stream details available.")

        live_chat_id = response["items"][0]["liveStreamingDetails"].get("activeLiveChatId")
        if not live_chat_id:
            raise Exception("This video does not have an active live chat.")

        print(f"✅ Found Live Chat ID: {live_chat_id}")
        return live_chat_id

    def poll_chat(self):
        """Polls the live chat for new messages and puts them in the queue."""
        request = self.youtube.liveChatMessages().list(
            liveChatId=self.live_chat_id,
            part="snippet,authorDetails",
            maxResults=2000
        )
        response = request.execute()

        for item in response.get("items", []):
            # We can add more sophisticated timestamp checking later
            # For now, we'll just process all messages we see
            author = item["authorDetails"]["displayName"]
            message = item["snippet"]["displayMessage"]
            self.message_queue.put(f"{author}: {message}")

        # Wait a bit before the next poll to respect API rate limits
        time.sleep(5)

    def start_polling(self):
        """Starts a background thread to continuously poll the chat."""
        import threading
        print("▶️ Starting YouTube chat polling...")
        poll_thread = threading.Thread(target=self._poll_worker, daemon=True)
        poll_thread.start()

    def _poll_worker(self):
        """The worker function that runs in the background."""
        while True:
            try:
                self.poll_chat()
            except Exception as e:
                print(f"🚨 Error polling YouTube chat: {e}")
                time.sleep(15) # Wait longer on error