"""
Assignment 23: Set Timer and Provide Spoken Feedback
======================================================
Use Text-to-Speech to provide voice feedback when setting and completing timers.

Workflow:
1. User says: "set a timer for 5 minutes"
2. Speech recognized → sent to Assignment 22 function
3. Function returns: 300 seconds
4. System says: "Your 5 minute timer is set"
5. Timer counts down in background
6. When finished: "Your timer is finished"

Author: [Your Name]
Date: 2024
"""

import os
import time
import threading
import requests
import json
import logging
from typing import Optional
from dotenv import load_dotenv

# Azure Speech SDK
try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("ERROR: azure-cognitiveservices-speech not installed")
    print("Install with: pip install azure-cognitiveservices-speech")

# Load environment variables
load_dotenv()


# ============================================================================
# CONFIGURATION
# ============================================================================

# Azure Speech Service
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION", "eastus")

# Assignment 22 REST endpoint
TEXT_TO_TIMER_ENDPOINT = os.getenv("TEXT_TO_TIMER_ENDPOINT", "http://localhost:7071/api/text-to-timer")

# TTS Voice (see https://docs.microsoft.com/azure/cognitive-services/speech-service/language-support#text-to-speech)
TTS_VOICE = os.getenv("TTS_VOICE", "en-US-AriaNeural")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# TIMER CLASS
# ============================================================================

class SmartTimer:
    """Manages timer with background countdown"""
    
    def __init__(self, name: str = "default", duration_seconds: int = 0):
        self.name = name
        self.duration = duration_seconds
        self.remaining = duration_seconds
        self.is_running = False
        self.is_finished = False
        self.thread = None
    
    def start(self):
        """Start timer in background thread"""
        if self.is_running:
            logger.warning(f"Timer '{self.name}' is already running")
            return
        
        self.is_running = True
        self.is_finished = False
        self.remaining = self.duration
        
        # Start countdown in background thread
        self.thread = threading.Thread(target=self._countdown, daemon=True)
        self.thread.start()
        logger.info(f"Timer '{self.name}' started for {self.duration} seconds")
    
    def _countdown(self):
        """Countdown timer (runs in background)"""
        while self.remaining > 0 and self.is_running:
            time.sleep(1)
            self.remaining -= 1
            
            # Log every 10 seconds or at end
            if self.remaining % 10 == 0 or self.remaining == 0:
                logger.info(f"Timer '{self.name}': {self.remaining}s remaining")
        
        if self.remaining <= 0 and self.is_running:
            self.is_finished = True
            self.is_running = False
            logger.info(f"Timer '{self.name}' finished!")
    
    def stop(self):
        """Stop timer"""
        self.is_running = False
        logger.info(f"Timer '{self.name}' stopped")
    
    def check_status(self) -> dict:
        """Get timer status"""
        return {
            "name": self.name,
            "duration": self.duration,
            "remaining": self.remaining,
            "is_running": self.is_running,
            "is_finished": self.is_finished
        }


# ============================================================================
# TEXT-TO-SPEECH FUNCTIONS
# ============================================================================

def format_duration(seconds: int) -> str:
    """
    Convert seconds to readable format.
    
    Args:
        seconds: Total seconds
        
    Returns:
        str: Formatted time (e.g., "5 minutes" or "1 minute 30 seconds")
    """
    minutes = seconds // 60
    secs = seconds % 60
    
    if minutes == 0:
        if secs == 1:
            return "1 second"
        return f"{secs} seconds"
    
    if secs == 0:
        if minutes == 1:
            return "1 minute"
        return f"{minutes} minutes"
    
    # Both minutes and seconds
    min_str = "1 minute" if minutes == 1 else f"{minutes} minutes"
    sec_str = "1 second" if secs == 1 else f"{secs} seconds"
    return f"{min_str} {sec_str}"


def text_to_speech(text: str, voice: str = TTS_VOICE) -> Optional[bytes]:
    """
    Convert text to speech using Azure Speech Service.
    
    Args:
        text: Text to convert to speech
        voice: Voice name (e.g., "en-US-AriaNeural")
        
    Returns:
        bytes: Audio data, or None if failed
    """
    if not SPEECH_KEY:
        logger.error("SPEECH_KEY not configured")
        return None
    
    try:
        # Setup speech config
        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY,
            region=SPEECH_REGION
        )
        
        # Use specified voice
        speech_config.speech_synthesis_voice_name = voice
        
        # Configure to return audio bytes
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        
        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        # Create SSML with voice control
        ssml = f"""
        <speak version='1.0' xml:lang='en-US'>
            <voice name='{voice}'>
                {text}
            </voice>
        </speak>
        """
        
        logger.info(f"Converting to speech: {text}")
        
        # Synthesize
        result = synthesizer.speak_ssml_async(ssml).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info("✓ Speech synthesis successful")
            return result.audio_data
        
        elif result.reason == speechsdk.ResultReason.Canceled:
            error = result.cancellation_details
            logger.error(f"Speech synthesis canceled: {error.error_details}")
            return None
    
    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}")
        return None


# ============================================================================
# REST API FUNCTIONS
# ============================================================================

def call_text_to_timer(text: str, endpoint: str = TEXT_TO_TIMER_ENDPOINT) -> Optional[int]:
    """
    Call Assignment 22 REST endpoint to get timer duration.
    
    Args:
        text: User's spoken request
        endpoint: REST endpoint URL
        
    Returns:
        int: Timer duration in seconds, or None if failed
    """
    try:
        logger.info(f"Calling REST endpoint: {endpoint}")
        logger.info(f"With text: {text}")
        
        response = requests.post(
            endpoint,
            json={"text": text},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            seconds = data.get("seconds")
            logger.info(f"✓ Got {seconds} seconds from endpoint")
            return seconds
        
        elif response.status_code == 404:
            logger.warning("Intent not recognized (404)")
            return None
        
        else:
            logger.error(f"REST error: {response.status_code}")
            return None
    
    except requests.exceptions.Timeout:
        logger.error("REST request timeout")
        return None
    
    except Exception as e:
        logger.error(f"Error calling REST endpoint: {e}")
        return None


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

def set_timer_from_speech(recognized_text: str) -> bool:
    """
    Complete workflow: speech → understand → set timer → feedback.
    
    Args:
        recognized_text: Text from speech recognition
        
    Returns:
        bool: True if successful
    """
    
    print("\n" + "="*60)
    print("SETTING TIMER FROM SPEECH")
    print("="*60)
    
    logger.info(f"\n1. Recognized text: '{recognized_text}'")
    
    # Step 1: Get timer duration from REST endpoint (Assignment 22)
    print("\n[1/4] Sending to language understanding...")
    seconds = call_text_to_timer(recognized_text)
    
    if seconds is None:
        logger.error("Could not understand timer request")
        # Provide feedback
        text_to_speech("Sorry, I didn't understand. Please say 'set a timer for' followed by a time.")
        return False
    
    # Step 2: Format time for speech
    print(f"\n[2/4] Timer duration: {seconds} seconds")
    duration_text = format_duration(seconds)
    logger.info(f"Formatted duration: {duration_text}")
    
    # Step 3: Provide confirmation speech
    print(f"\n[3/4] Playing confirmation: 'Your {duration_text} timer is set'")
    confirmation_msg = f"Your {duration_text} timer is set"
    text_to_speech(confirmation_msg)
    
    # Step 4: Start timer
    print(f"\n[4/4] Starting {duration_text} countdown...")
    timer = SmartTimer(name="user_timer", duration_seconds=seconds)
    timer.start()
    
    # Wait for timer to finish
    print("\nTimer running... (Ctrl+C to cancel)")
    try:
        while timer.is_running:
            time.sleep(1)
        
        # Timer finished
        logger.info("Timer finished!")
        alert_msg = f"Your {duration_text} timer is finished"
        text_to_speech(alert_msg)
        print(f"\n✓ Alert: {alert_msg}")
        
    except KeyboardInterrupt:
        print("\n⏸ Timer cancelled")
        timer.stop()
        text_to_speech("Timer cancelled")
        return False
    
    return True


# ============================================================================
# SIMPLE TEST
# ============================================================================

def main():
    """Main program for testing"""
    
    print("\n" + "="*60)
    print("Assignment 23: Set Timer with Spoken Feedback")
    print("="*60)
    
    # Example: Set a 30-second timer for quick testing
    test_text = "set a timer for 30 seconds"
    
    print(f"\nTest scenario: '{test_text}'")
    print("\nNote: Make sure Assignment 22 endpoint is running!")
    print(f"Expected endpoint: {TEXT_TO_TIMER_ENDPOINT}")
    
    success = set_timer_from_speech(test_text)
    
    if success:
        print("\n✓ SUCCESS!")
    else:
        print("\n✗ FAILED")


if __name__ == "__main__":
    main()
