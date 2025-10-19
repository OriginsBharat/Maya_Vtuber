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

    def extract_audio(self, video_path: str, output_audio_path: str):
        """Extracts the audio from a video file."""
        try:
            print(f"Extracting audio from '{video_path}'...")
            command = [
                'ffmpeg',
                '-y',
                '-i', video_path,
                '-vn', # No video
                '-acodec', 'copy', # Copy audio codec
                output_audio_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            print(f"✅ Audio extracted successfully to '{output_audio_path}'")
            return output_audio_path
        except subprocess.CalledProcessError as e:
            print(f"🚨 Error extracting audio: {e.stderr.decode()}")
            return None

    def replace_audio(self, video_path: str, new_audio_path: str, output_path: str):
        """Replaces the audio track of a video with a new one."""
        try:
            print(f"Replacing audio in '{video_path}' with '{new_audio_path}'...")
            command = [
                'ffmpeg',
                '-y',
                '-i', video_path,
                '-i', new_audio_path,
                '-c:v', 'copy', # Copy video stream
                '-c:a', 'aac',    # Re-encode new audio
                '-map', '0:v:0', # Map video from first input
                '-map', '1:a:0', # Map audio from second input
                '-shortest',
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            print(f"✅ Dubbed video created successfully at '{output_path}'")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"🚨 Error replacing audio: {e.stderr.decode()}")
            return None

    def stitch_videos(self, clip_paths: list, output_path: str):
        """
        Stitches multiple video clips together into a single video.

        Args:
            clip_paths: A list of paths to the video clips to stitch.
            output_path: Path to save the final stitched video.
        """
        try:
            print(f"Stitching {len(clip_paths)} clips together...")

            # Create a temporary file listing all the clips to be concatenated
            with open("concat_list.txt", "w") as f:
                for path in clip_paths:
                    f.write(f"file '{path}'\n")

            command = [
                'ffmpeg',
                '-y',
                '-f', 'concat', # Use the concat demuxer
                '-safe', '0',   # Allow unsafe file paths
                '-i', 'concat_list.txt',
                '-c', 'copy',   # Copy codecs to avoid re-encoding
                output_path
            ]

            subprocess.run(command, check=True, capture_output=True)

            # Clean up the temporary file list
            import os
            os.remove("concat_list.txt")

            print(f"✅ Video stitched successfully at '{output_path}'")
            return output_path

        except subprocess.CalledProcessError as e:
            print(f"🚨 An error occurred during video stitching: {e.stderr.decode()}")
            return None