import speech_recognition as sr
import queue
import threading
import time

class AudioListener:
    """
    Listens for audio from the microphone and transcribes it to text.
    """
    def __init__(self, text_queue: queue.Queue):
        """
        Initializes the audio listener.

        Args:
            text_queue: A queue to put the transcribed text into.
        """
        self.r = sr.Recognizer()
        self.text_queue = text_queue
        print("🎤 Audio Listener initialized.")

    def listen_continuously(self):
        """Starts a background thread to listen for audio continuously."""
        listen_thread = threading.Thread(target=self._listen_worker, daemon=True)
        listen_thread.start()
        print("▶️ Started listening for director's voice commands...")

    def _listen_worker(self):
        """The worker function that runs in the background."""
        with sr.Microphone() as source:
            # Adjust for ambient noise once at the start
            print("🤫 Adjusting for ambient noise, please be quiet...")
            self.r.adjust_for_ambient_noise(source, duration=2)
            print("✅ Ready for your voice commands.")

            while True:
                try:
                    audio = self.r.listen(source)
                    # Use Google's free web speech API for transcription
                    text = self.r.recognize_google(audio)
                    print(f"🎤 Director Said: '{text}'")
                    self.text_queue.put(text)
                except sr.UnknownValueError:
                    # This is fine, it just means there was silence
                    pass
                except sr.RequestError as e:
                    print(f"🚨 Could not request results from Google Speech Recognition service; {e}")
                    # Wait a bit before trying again
                    time.sleep(5)
                except Exception as e:
                    print(f"🚨 An unknown error occurred in audio listener: {e}")
                    time.sleep(5)