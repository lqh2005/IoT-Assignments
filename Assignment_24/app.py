"""
Assignment 24: Support Multiple Languages
===========================================
Add multilingual support to the smart timer using Azure Translator.

Complete workflow with language translation:
1. User speaks in any language (e.g., French)
2. Auto-detect or select language
3. Translate to English
4. Process timer (Assignment 22)
5. Translate response back to user's language
6. Speak with appropriate TTS voice

Author: [Your Name]
Date: 2024
"""

import os
import requests
import json
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

# Azure Translator Service
TRANSLATOR_KEY = os.getenv("TRANSLATOR_KEY")
TRANSLATOR_ENDPOINT = os.getenv("TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
TRANSLATOR_REGION = os.getenv("TRANSLATOR_REGION", "eastus")

# Other services
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION", "eastus")
TEXT_TO_TIMER_ENDPOINT = os.getenv("TEXT_TO_TIMER_ENDPOINT", "http://localhost:7071/api/text-to-timer")

# Default language for processing
PROCESSING_LANGUAGE = "en"


# ============================================================================
# LANGUAGE CONFIGURATION
# ============================================================================

# TTS Voice mapping by language
VOICE_MAP = {
    "en": "en-US-AriaNeural",
    "es": "es-ES-ConchitaNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-SeraphinaNeural",
    "it": "it-IT-IsabellaNeural",
    "pt": "pt-BR-ThalitaNeural",
    "zh-Hans": "zh-CN-XiaoxiaoNeural",
    "ja": "ja-JP-NanamisNeural",
    "ko": "ko-KR-SunHiNeural",
    "ar": "ar-SA-ZariyahNeural",
}

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "zh-Hans": "Chinese (Simplified)",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "ru": "Russian",
    "tr": "Turkish",
}


# ============================================================================
# TRANSLATOR FUNCTIONS
# ============================================================================

def detect_language(text: str) -> Optional[str]:
    """
    Detect language of given text using Azure Translator.
    
    Args:
        text: Text to detect language for
        
    Returns:
        str: Language code (e.g., 'en', 'fr'), or None if failed
    """
    if not TRANSLATOR_KEY:
        logger.error("TRANSLATOR_KEY not configured")
        return None
    
    try:
        url = f"{TRANSLATOR_ENDPOINT}/detect?api-version=3.0"
        headers = {
            "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
            "Ocp-Apim-Subscription-Region": TRANSLATOR_REGION,
            "Content-Type": "application/json"
        }
        
        body = [{"text": text}]
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result and len(result) > 0:
            language = result[0].get("language")
            logger.info(f"Detected language: {language}")
            return language
        
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
    
    return None


def translate_text(text: str, source_lang: str, target_lang: str) -> Optional[str]:
    """
    Translate text from source to target language using Azure Translator.
    
    Args:
        text: Text to translate
        source_lang: Source language code (e.g., 'fr')
        target_lang: Target language code (e.g., 'en')
        
    Returns:
        str: Translated text, or None if failed
    """
    if not TRANSLATOR_KEY:
        logger.error("TRANSLATOR_KEY not configured")
        return None
    
    try:
        url = f"{TRANSLATOR_ENDPOINT}/translate?api-version=3.0&from={source_lang}&to={target_lang}"
        headers = {
            "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
            "Ocp-Apim-Subscription-Region": TRANSLATOR_REGION,
            "Content-Type": "application/json"
        }
        
        body = [{"text": text}]
        
        logger.info(f"Translating '{text}' from {source_lang} to {target_lang}")
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result and len(result) > 0:
            translated = result[0].get("translations", [{}])[0].get("text")
            logger.info(f"Translation result: {translated}")
            return translated
        
    except Exception as e:
        logger.error(f"Error translating text: {e}")
    
    return None


def get_voice_for_language(language_code: str) -> str:
    """
    Get appropriate TTS voice for language.
    
    Args:
        language_code: Language code (e.g., 'en', 'fr', 'es')
        
    Returns:
        str: Voice name, or default if not found
    """
    voice = VOICE_MAP.get(language_code, VOICE_MAP["en"])
    logger.info(f"Using voice for {language_code}: {voice}")
    return voice


def list_supported_languages() -> dict:
    """Get dictionary of supported languages"""
    return SUPPORTED_LANGUAGES


# ============================================================================
# MULTILINGUAL WORKFLOW
# ============================================================================

def set_multilingual_timer(user_input: str, user_language: Optional[str] = None) -> bool:
    """
    Complete multilingual timer workflow.
    
    Args:
        user_input: User's input in their language
        user_language: User's language (auto-detect if None)
        
    Returns:
        bool: True if successful
    """
    
    print("\n" + "="*60)
    print("MULTILINGUAL SMART TIMER")
    print("="*60)
    
    # Step 1: Detect or use provided language
    print("\n[1/6] Detecting language...")
    if user_language:
        detected_language = user_language
        logger.info(f"Using provided language: {detected_language}")
    else:
        detected_language = detect_language(user_input)
        if not detected_language:
            logger.error("Could not detect language")
            return False
    
    if detected_language not in SUPPORTED_LANGUAGES:
        logger.error(f"Language {detected_language} not supported")
        print(f"Supported: {list(SUPPORTED_LANGUAGES.keys())}")
        return False
    
    language_name = SUPPORTED_LANGUAGES[detected_language]
    print(f"✓ Language: {language_name} ({detected_language})")
    
    # Step 2: Translate to English for processing
    print(f"\n[2/6] Translating from {language_name} to English...")
    if detected_language != PROCESSING_LANGUAGE:
        english_text = translate_text(
            user_input,
            source_lang=detected_language,
            target_lang=PROCESSING_LANGUAGE
        )
        if not english_text:
            logger.error("Translation failed")
            return False
    else:
        english_text = user_input
    
    print(f"✓ English text: '{english_text}'")
    
    # Step 3: Call Assignment 22 (NLU in English)
    print(f"\n[3/6] Processing timer request...")
    try:
        response = requests.post(
            TEXT_TO_TIMER_ENDPOINT,
            json={"text": english_text},
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"Timer endpoint returned {response.status_code}")
            return False
        
        data = response.json()
        seconds = data.get("seconds")
        print(f"✓ Timer duration: {seconds} seconds")
        
    except Exception as e:
        logger.error(f"Error calling timer endpoint: {e}")
        return False
    
    # Step 4: Format duration in English
    print(f"\n[4/6] Formatting confirmation message...")
    minutes = seconds // 60
    secs = seconds % 60
    
    if minutes > 0 and secs > 0:
        duration_str = f"{minutes} minute{'s' if minutes > 1 else ''} {secs} second{'s' if secs > 1 else ''}"
    elif minutes > 0:
        duration_str = f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        duration_str = f"{secs} second{'s' if secs > 1 else ''}"
    
    english_message = f"Your {duration_str} timer is set"
    print(f"English message: '{english_message}'")
    
    # Step 5: Translate response back to user's language
    print(f"\n[5/6] Translating response to {language_name}...")
    if detected_language != PROCESSING_LANGUAGE:
        user_message = translate_text(
            english_message,
            source_lang=PROCESSING_LANGUAGE,
            target_lang=detected_language
        )
        if not user_message:
            logger.error("Response translation failed")
            user_message = english_message  # Fallback
    else:
        user_message = english_message
    
    print(f"✓ Message in {language_name}: '{user_message}'")
    
    # Step 6: TTS with appropriate voice
    print(f"\n[6/6] Speaking confirmation...")
    voice = get_voice_for_language(detected_language)
    logger.info(f"Would use voice: {voice} (speech synthesis not included in this demo)")
    print(f"✓ TTS voice: {voice}")
    
    print(f"\n{'='*60}")
    print("COMPLETE WORKFLOW:")
    print(f"  Input ({language_name}): {user_input}")
    print(f"  → English (processing): {english_text}")
    print(f"  → Timer: {seconds} seconds")
    print(f"  → Response ({language_name}): {user_message}")
    print(f"  → Voice: {voice}")
    print(f"{'='*60}")
    
    return True


# ============================================================================
# MAIN TEST
# ============================================================================

def main():
    """Test multilingual timer with different languages"""
    
    print("\nAssignment 24: Support Multiple Languages")
    print("="*60)
    
    # Test cases in different languages
    test_cases = [
        ("set a timer for 5 minutes", "en", "English"),
        ("mettre un minuteur pour 5 minutes", "fr", "French"),
        ("establecer un temporizador para 5 minutos", "es", "Spanish"),
        ("Stellen Sie einen Timer auf 5 Minuten ein", "de", "German"),
    ]
    
    print("\nSupported languages:")
    for code, name in SUPPORTED_LANGUAGES.items():
        print(f"  {code}: {name}")
    
    print("\nRunning tests...\n")
    
    for i, (input_text, lang_code, lang_name) in enumerate(test_cases, 1):
        print(f"\n{'#'*60}")
        print(f"Test {i}: {lang_name}")
        print(f"{'#'*60}")
        
        success = set_multilingual_timer(input_text, user_language=lang_code)
        
        if success:
            print(f"✓ Test {i} passed")
        else:
            print(f"✗ Test {i} failed")


if __name__ == "__main__":
    main()
