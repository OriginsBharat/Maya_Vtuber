from pathlib import Path
import torch
# We will need to add 'indextts' to our dependencies later.
# For now, we assume it's installed in the environment.
import simpleaudio as sa # A simple library for playing audio

class TTSManager:
    """
    Manages Text-to-Speech generation using the IndexTTS library.
    """
    def __init__(self, cfg_path: str, model_dir: str, use_fp16: bool = True):
        """
        Initializes the TTS model.

        Args:
            cfg_path: Path to the IndexTTS config.yaml file.
            model_dir: Path to the directory containing the IndexTTS model checkpoints.
            use_fp16: Whether to use half-precision for faster inference.
        """
        print("🔊 Initializing TTS Manager...")
        try:
            from indextts.infer_v2 import IndexTTS2
        except ImportError:
            raise ImportError(
                "The 'indextts' library is not installed. "
                "Please follow the manual installation instructions from its GitHub repository."
            )

        if not Path(model_dir).exists() or not Path(cfg_path).exists():
            raise FileNotFoundError(
                "TTS model directory or config not found. "
                "Please ensure you have downloaded the IndexTTS models into a 'checkpoints' directory."
            )

        self.tts_model = IndexTTS2(
            cfg_path=cfg_path,
            model_dir=model_dir,
            use_fp16=use_fp16,
            use_cuda_kernel=torch.cuda.is_available(),
            use_deepspeed=False # Deepspeed can be complex to set up
        )
        print("✅ TTS Model loaded.")

    def speak(self, text: str, voice_prompt_path: str, output_path: str = "output.wav", language: str = 'en'):
        """
        Generates speech from text using a voice prompt and plays it.

        Args:
            text: The text to be spoken.
            voice_prompt_path: Path to the .wav file to be used for voice cloning.
            output_path: The path to save the generated audio file.
            language: The language of the text (e.g., 'en', 'hi', 'zh-cn').
        """
        print(f"Synthesizing speech for: '{text}'")

        # Generate the audio file
        self.tts_model.infer(
            spk_audio_prompt=voice_prompt_path,
            text=text,
            output_path=output_path,
            verbose=False # Keep the console clean
        )

        print(f"Audio saved to {output_path}. Now playing...")

        # Play the generated audio file
        self._play_audio(output_path)

        print("Finished playing audio.")

    def _play_audio(self, file_path: str):
        """Plays a .wav file."""
        try:
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            play_obj = wave_obj.play()
            play_obj.wait_done()  # Wait until sound has finished playing
        except Exception as e:
            print(f"🚨 Error playing audio: {e}")
            print("🚨 Please ensure 'ffmpeg' is installed on your system if you see format errors.")
            print("🚨 On Debian/Ubuntu: sudo apt-get install ffmpeg")
            print("🚨 On MacOS (with Homebrew): brew install ffmpeg")