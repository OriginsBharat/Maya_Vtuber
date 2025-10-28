import os
import sys
import torch
import soundfile as sf
from loguru import logger
import time

from indextts.infer import IndexTTS
from maya_ai.config.config_loader import get_config

class TTSManager:
    """
    Manages Text-to-Speech generation using the Index TTS model.
    """
    def __init__(self):
        """
        Initializes the TTS Manager and loads the Index TTS model.
        """
        self.model = None
        self.config = get_config()
        self.load_model_with_retry()

    def load_model_with_retry(self, max_retries=3, delay=5):
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
                logger.info("Index TTS model loaded successfully.")
                return
            except Exception as e:
                logger.error(f"Error loading Index TTS model (attempt {attempt + 1}/{max_retries}): {e}", exc_info=True)
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("Failed to load Index TTS model after multiple retries.")
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
                verbose=True
            )
            logger.info(f"Speech generated and saved to {output_path}")
        except Exception as e:
            logger.error(f"Error during TTS generation: {e}", exc_info=True)
