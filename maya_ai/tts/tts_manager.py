import os
import sys
import torch
import soundfile as sf
from loguru import logger
import time

from indextts.infer import IndexTTS
from maya_ai.config.config_loader import get_config

# --- Constants ---
MAX_TTS_RETRIES = 3
TTS_RETRY_DELAY_SECONDS = 5

class TTSManager:
    """
    Manages Text-to-Speech generation using the Index TTS model.

    Setup Instructions (Crucial!):
    1.  This class depends on the Index TTS v1.9B model, which is a powerful but complex dependency.
        Official Repo: https://github.com/X-LANCE/Index-1.9B
    2.  Download the pre-trained models from Hugging Face:
        https://huggingface.co/X-LANCE/Index-1.9B-v2/tree/main
        - You need `config.yaml` and `pytorch_model.bin`.
    3.  Place these files in the `vendor/index-tts/checkpoints/` directory.
    4.  Ensure your `config.yaml` file in the project root points to these files.

    Troubleshooting:
    - If loading fails, double-check the model paths in your main `config.yaml`.
    - Ensure you have enough RAM (8GB+ is recommended).
    - If you get CUDA errors, try setting `use_fp16: false` in your `config.yaml`.
    """
    def __init__(self):
        """
        Initializes the TTS Manager and loads the Index TTS model.
        """
        self.model = None
        self.config = get_config()
        self.load_model_with_retry()

    def load_model_with_retry(self, max_retries=MAX_TTS_RETRIES, delay=TTS_RETRY_DELAY_SECONDS):
        """
        Loads the Index TTS model with retry logic.
        """
        for attempt in range(max_retries):
            try:
                use_fp16 = self.config.get('tts', 'use_fp16', default=torch.cuda.is_available())

                self.model = IndexTTS(
                    cfg_path=self.config.get('tts', 'config_path'),
                    model_dir=self.config.get('tts', 'model_dir'),
                    use_fp16=use_fp16
                )
                logger.success("✅ Index TTS model loaded successfully.")
                return
            except FileNotFoundError as e:
                logger.critical(
                    f"❌ TTS Model file not found. Please ensure the model files exist at the configured path. Error: {e}"
                    "Refer to the setup instructions in `tts_manager.py`."
                )
                self.model = None
                return # Do not retry on a clear file-not-found error
            except Exception as e:
                logger.error(f"Error loading Index TTS model (attempt {attempt + 1}/{max_retries}): {e}", exc_info=True)
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.critical("❌ Failed to load Index TTS model after multiple retries.")
                    self.model = None

    def speak(self, text: str, voice_reference_path: str, output_path: str = "output.wav", language: str = "en"):
        """
        Generates speech from text using a reference voice.
        """
        if self.model is None:
            logger.error("TTS model not loaded. Cannot generate speech.")
            return

        try:
            self.model.infer(
                spk_audio_prompt=voice_reference_path,
                text=text,
                output_path=output_path,
                language=language,
                verbose=True # Set to False to reduce console spam
            )
            logger.info(f"Speech generated and saved to {output_path}")
        except Exception as e:
            logger.error(f"Error during TTS generation: {e}", exc_info=True)
