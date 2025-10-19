import subprocess

class VideoEditor:
    """
    A simple video editor that uses ffmpeg directly to create a video.
    """
    def __init__(self):
        print("🎬 Video Editor initialized (using direct ffmpeg calls).")
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Checks if ffmpeg is installed and accessible."""
        try:
            subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
            print("✅ ffmpeg is available.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "ffmpeg not found. Please ensure ffmpeg is installed and in your system's PATH."
            )

    def create_video(self, image_path: str, audio_path: str, output_path: str):
        """
        Creates a video by combining a static image and an audio file using ffmpeg.

        Args:
            image_path: Path to the input image file.
            audio_path: Path to the input audio file.
            output_path: Path to save the final .mp4 video.
        """
        try:
            print(f"Creating video from '{image_path}' and '{audio_path}' using ffmpeg...")

            command = [
                'ffmpeg',
                '-y',           # Overwrite output file if it exists
                '-loop', '1',   # Loop the input image
                '-i', image_path, # Input image
                '-i', audio_path, # Input audio
                '-c:v', 'libx264', # Video codec
                '-tune', 'stillimage', # Optimize for static image
                '-c:a', 'aac',    # Audio codec
                '-b:a', '192k',   # Audio bitrate
                '-pix_fmt', 'yuv420p', # Pixel format for compatibility
                '-shortest',    # Finish encoding when the shortest input stream ends (the audio)
                output_path
            ]

            subprocess.run(command, check=True, capture_output=True)

            print(f"✅ Video created successfully at '{output_path}'")
            return output_path

        except subprocess.CalledProcessError as e:
            print(f"🚨 An error occurred during video creation with ffmpeg.")
            print(f"🚨 Command: {' '.join(command)}")
            print(f"🚨 Stderr: {e.stderr.decode()}")
            return None
        except Exception as e:
            print(f"🚨 An unexpected error occurred: {e}")
            return None