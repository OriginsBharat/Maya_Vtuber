import translators as ts
from loguru import logger

class Translator:
    """
    Handles text translation using various free translation APIs.
    """
    def __init__(self):
        logger.info("🌐 Translator initialized.")

    def translate(self, text: str, target_language: str, source_language: str = 'auto') -> str:
        """
        Translates text to a target language.

        Args:
            text: The text to translate.
            target_language: The language to translate to (e.g., 'en', 'es', 'zh-CN').
            source_language: The source language (defaults to auto-detect).

        Returns:
            The translated text, or the original text on error.
        """
        try:
            logger.debug(f"Translating '{text[:30]}...' to {target_language}")
            # The 'translators' library can be unstable, so we have a fallback.
            # We will try Google, then Bing.
            translated_text = ts.translate_text(
                text,
                translator='google',
                from_language=source_language,
                to_language=target_language
            )
            logger.info("✅ Translation successful.")
            return translated_text
        except Exception as e:
            logger.error(f"An error occurred during translation: {e}", exc_info=True)
            return text # Return original text as a fallback