import subprocess
from loguru import logger

class VideoEditor:
    """
    A simple video editor that uses ffmpeg directly to create a video.
    """
    def __init__(self):
        logger.info("🎬 Video Editor initialized (using direct ffmpeg calls).")
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Checks if ffmpeg is installed and accessible."""
        try:
            subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
            logger.info("✅ ffmpeg is available.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "ffmpeg not found. Please ensure ffmpeg is installed and in your system's PATH."
            )

    def create_video(self, image_path: str, audio_path: str, output_path: str):
        """
        Creates a video by combining a static image and an audio file using ffmpeg.
        """
        try:
            logger.info(f"Creating video from '{image_path}' and '{audio_path}' using ffmpeg...")

            command = [
                'ffmpeg',
                '-y',
                '-loop', '1',
                '-i', image_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-tune', 'stillimage',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                output_path
            ]

            subprocess.run(command, check=True, capture_output=True)

            logger.info(f"✅ Video created successfully at '{output_path}'")
            return output_path

        except subprocess.CalledProcessError as e:
            logger.error(f"🚨 An error occurred during video creation with ffmpeg.")
            logger.error(f"🚨 Command: {' '.join(command)}")
            logger.error(f"🚨 Stderr: {e.stderr.decode()}")
            return None
        except Exception as e:
            logger.error(f"🚨 An unexpected error occurred: {e}", exc_info=True)
            return None

    def extract_audio(self, video_path: str, output_audio_path: str):
        """Extracts the audio from a video file."""
        try:
            logger.info(f"Extracting audio from '{video_path}'...")
            command = [
                'ffmpeg',
                '-y',
                '-i', video_path,
                '-vn',
                '-acodec', 'copy',
                output_audio_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            logger.info(f"✅ Audio extracted successfully to '{output_audio_path}'")
            return output_audio_path
        except subprocess.CalledProcessError as e:
            logger.error(f"🚨 Error extracting audio: {e.stderr.decode()}")
            return None

    def replace_audio(self, video_path: str, new_audio_path: str, output_path: str):
        """Replaces the audio track of a video with a new one."""
        try:
            logger.info(f"Replacing audio in '{video_path}' with '{new_audio_path}'...")
            command = [
                'ffmpeg',
                '-y',
                '-i', video_path,
                '-i', new_audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            logger.info(f"✅ Dubbed video created successfully at '{output_path}'")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"🚨 Error replacing audio: {e.stderr.decode()}")
            return None

    def stitch_videos(self, clip_paths: list, output_path: str):
        """
        Stitches multiple video clips together into a single video.
        """
        try:
            logger.info(f"Stitching {len(clip_paths)} clips together...")

            with open("concat_list.txt", "w") as f:
                for path in clip_paths:
                    f.write(f"file '{path}'\n")

            command = [
                'ffmpeg',
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', 'concat_list.txt',
                '-c', 'copy',
                output_path
            ]

            subprocess.run(command, check=True, capture_output=True)

            import os
            os.remove("concat_list.txt")

            logger.info(f"✅ Video stitched successfully at '{output_path}'")
            return output_path

        except subprocess.CalledProcessError as e:
            logger.error(f"🚨 An error occurred during video stitching: {e.stderr.decode()}")
            return None
