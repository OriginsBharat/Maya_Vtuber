import os
import sys
import torch
import soundfile as sf

# --- HACK: Add the vendor directory to the Python path ---
# This is necessary because the index-tts project is not a standard package.
# We need to do this to be able to import its modules.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'vendor', 'index-tts'))
# --- END HACK ---

from indextts.infer_v2 import IndexTTS2

class TTSManager:
    """
    Manages Text-to-Speech generation using the Index TTS model.
    """
    def __init__(self):
        """
        Initializes the TTS Manager and loads the Index TTS model.
        """
        self.model = None
        self.load_model()

    def load_model(self):
        """
        Loads the Index TTS model from the vendor directory.
        """
        try:
            # Determine if a CUDA-enabled GPU is available
            use_fp16 = torch.cuda.is_available()

            # Configuration for the model, pointing to the downloaded checkpoints
            self.model = IndexTTS2(
                cfg_path="vendor/index-tts/checkpoints/config.yaml",
                model_dir="vendor/index-tts/checkpoints",
                use_fp16=use_fp16,  # Use half-precision if a GPU is available
                use_cuda_kernel=torch.cuda.is_available(),
                use_deepspeed=False # Disabled for Windows compatibility
            )
            print("Index TTS model loaded successfully.")
        except Exception as e:
            print(f"Error loading Index TTS model: {e}")
            self.model = None

    def speak(self, text: str, voice_reference_path: str, output_path: str = "output.wav"):
        """
        Generates speech from text using a reference voice.

        Args:
            text: The text to be converted to speech.
            voice_reference_path: Path to a .wav file to be used as a voice reference.
            output_path: The path to save the generated audio file.
        """
        if self.model is None:
            print("TTS model not loaded. Cannot generate speech.")
            return

        try:
            self.model.infer(
                spk_audio_prompt=voice_reference_path,
                text=text,
                output_path=output_path,
                verbose=True
            )
            print(f"Speech generated and saved to {output_path}")
        except Exception as e:
            print(f"Error during TTS generation: {e}")

# Example usage (for testing)
if __name__ == '__main__':
    # We need some dummy voice references to test with.
    # In the real application, these will be the voices for Sarjana and Durjana.
    if not os.path.exists("sarjana_ref.wav"):
        print("Creating dummy voice reference for Sarjana.")
        # Create a silent 1-second wav file
        sf.write("sarjana_ref.wav", [0]*16000, 16000)

    if not os.path.exists("durjana_ref.wav"):
        print("Creating dummy voice reference for Durjana.")
        sf.write("durjana_ref.wav", [0]*16000, 16000)

    tts_manager = TTSManager()
    if tts_manager.model:
        print("\n--- Testing Sarjana's Voice ---")
        tts_manager.speak("Hello, I am Sarjana. It is a pleasure to meet you.", "sarjana_ref.wav", "sarjana_test.wav")

        print("\n--- Testing Durjana's Voice ---")
        tts_manager.speak("Hey, I'm Durjana. What's up?", "durjana_ref.wav", "durjana_test.wav")
