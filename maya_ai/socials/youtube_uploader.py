import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

class YouTubeUploader:
    """
    Handles uploading videos to YouTube.
    """
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    def __init__(self, client_secrets_path: str = 'client_secrets.json', credentials_path: str = 'youtube_token.pickle'):
        self.client_secrets_path = client_secrets_path
        self.credentials_path = credentials_path
        self.youtube = None # Defer authentication

    def _get_authenticated_service(self):
        """Authenticates and returns a YouTube API service object, only when needed."""
        if self.youtube:
            return self.youtube
        """Authenticate and return a YouTube API service object."""
        creds = None
        if os.path.exists(self.credentials_path):
            with open(self.credentials_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.client_secrets_path):
                    raise FileNotFoundError(
                        f"'{self.client_secrets_path}' not found. Please download your "
                        "Google Cloud credentials for YouTube Data API v3."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_path, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.credentials_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('youtube', 'v3', credentials=creds)

    def upload_video(self, file_path: str, title: str, description: str, tags: list = None):
        """
        Uploads a video to YouTube.

        Args:
            file_path: Path to the video file.
            title: The title of the video.
            description: The description of the video.
            tags: A list of tags for the video.
        """
        if not os.path.exists(file_path):
            print(f"🚨 Video file not found: {file_path}")
            return None

        try:
            # Authenticate only when an upload is requested
            self.youtube = self._get_authenticated_service()
            if not self.youtube:
                return None

            print(f"⬆️ Uploading '{file_path}' to YouTube...")
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '20' # 20 is for Gaming, adjust as needed
                },
                'status': {
                    'privacyStatus': 'private' # 'public', 'private', or 'unlisted'
                }
            }

            media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%.")

            print(f"✅ Video uploaded successfully! Video ID: {response.get('id')}")
            return response.get('id')

        except Exception as e:
            print(f"🚨 An error occurred during YouTube upload: {e}")
            return None