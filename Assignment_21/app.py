"""
Assignment 21: Recognize Speech with an IoT Device
====================================================
Learn to capture audio from a microphone and convert speech to text 
using Azure Cognitive Services.

Author: [Your Name]
Date: 2024
Platform: [Choose: Wio Terminal / Raspberry Pi / Virtual Device]
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure Speech SDK
try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("ERROR: azure-cognitiveservices-speech not installed")
    print("Install with: pip install azure-cognitiveservices-speech")
    sys.exit(1)

# Audio capture libraries
try:
    import pyaudio
    import numpy as np
    import soundfile as sf
except ImportError:
    print("ERROR: Required audio libraries not installed")
    print("Install with: pip install pyaudio numpy soundfile")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================

# Azure Speech Service credentials
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION", "eastus")

# Audio recording parameters
SAMPLE_RATE = 16000  # 16 kHz (standard for speech recognition)
AUDIO_DURATION = 5   # seconds (how long to record)
CHANNELS = 1         # Mono
CHUNK_SIZE = 1024    # Samples per chunk
AUDIO_FORMAT = 16    # 16-bit
AUDIO_FILE = "recorded_audio.wav"


# ============================================================================
# TASK 2: SETUP MICROPHONE & SPEAKERS
# ============================================================================

def setup_microphone():
    """
    Configure microphone and speakers for audio I/O.
    
    Returns:
        dict: Audio device information
    """
    print("\n" + "="*60)
    print("TASK 2: Setting Up Microphone & Speakers")
    print("="*60)
    
    try:
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # List available audio devices
        print(f"\nFound {p.get_device_count()} audio devices:")
        print("-" * 60)
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            device_type = "INPUT" if info['maxInputChannels'] > 0 else "OUTPUT"
            print(f"[{i}] {info['name'][:40]:40} ({device_type})")
        
        # Use default microphone
        default_mic = p.get_default_input_device_info()
        default_speaker = p.get_default_output_device_info()
        
        print("\n" + "-" * 60)
        print(f"Default Microphone: [{default_mic['index']}] {default_mic['name']}")
        print(f"Default Speaker:   [{default_speaker['index']}] {default_speaker['name']}")
        print("-" * 60)
        
        return {"pyaudio": p, "mic_index": default_mic['index']}
        
    except Exception as e:
        print(f"ERROR: Failed to setup microphone: {e}")
        return None


# ============================================================================
# TASK 3: CAPTURE AUDIO FROM MICROPHONE
# ============================================================================

def capture_audio(duration=AUDIO_DURATION, filename=AUDIO_FILE):
    """
    Record audio from microphone and save as WAV file.
    
    Args:
        duration (int): Recording duration in seconds
        filename (str): Output WAV filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    print("\n" + "="*60)
    print("TASK 3: Capturing Audio from Microphone")
    print("="*60)
    
    try:
        # Setup audio
        audio_info = setup_microphone()
        if not audio_info:
            return False
            
        p = audio_info["pyaudio"]
        
        print(f"\nRecording {duration} seconds of audio...")
        print(f"Sample Rate: {SAMPLE_RATE} Hz")
        print(f"Channels: {CHANNELS}")
        print(f"Format: 16-bit")
        print(f"Output: {filename}")
        print("-" * 60)
        
        # Open audio stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        # Record audio frames
        frames = []
        for i in range(0, int(SAMPLE_RATE / CHUNK_SIZE * duration)):
            data = stream.read(CHUNK_SIZE)
            frames.append(data)
            
            # Show progress
            progress = (i + 1) / (SAMPLE_RATE / CHUNK_SIZE * duration)
            bar = "█" * int(progress * 30)
            print(f"\rRecording: [{bar:30}] {progress*100:.0f}%", end="")
        
        print("\n✓ Recording complete!")
        
        # Stop stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Convert byte data to numpy array
        audio_data = b''.join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Save to WAV file
        sf.write(filename, audio_array, SAMPLE_RATE)
        
        file_size = os.path.getsize(filename) / 1024  # KB
        print(f"✓ Saved to: {filename} ({file_size:.1f} KB)")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to capture audio: {e}")
        return False


# ============================================================================
# TASK 4 & 5: CONVERT SPEECH TO TEXT
# ============================================================================

def recognize_speech(audio_file=AUDIO_FILE):
    """
    Convert speech in audio file to text using Azure Speech Service.
    
    Args:
        audio_file (str): Path to WAV file
        
    Returns:
        str: Transcribed text or None if failed
    """
    print("\n" + "="*60)
    print("TASK 4 & 5: Converting Speech to Text")
    print("="*60)
    
    # Validate credentials
    if not SPEECH_KEY:
        print("\nERROR: SPEECH_KEY not found in .env file")
        print("Please create .env with:")
        print("  SPEECH_KEY=your_api_key_here")
        print("  SPEECH_REGION=eastus")
        return None
    
    # Check if audio file exists
    if not os.path.exists(audio_file):
        print(f"\nERROR: Audio file not found: {audio_file}")
        return None
    
    print(f"\nAzure Speech Configuration:")
    print(f"  Region: {SPEECH_REGION}")
    print(f"  API Key: {SPEECH_KEY[:10]}...****")
    print(f"  Audio File: {audio_file}")
    print("-" * 60)
    
    try:
        # Setup Azure Speech Service
        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY,
            region=SPEECH_REGION
        )
        
        # Configure for WAV file input
        audio_config = speechsdk.audio.AudioConfig(
            filename=audio_file
        )
        
        # Create speech recognizer
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        print("\nProcessing audio...")
        print("-" * 60)
        
        # Recognize speech from audio file
        result = speech_recognizer.recognize_once()
        
        # Check result
        if result.reason == speechsdk.ResultReason.RecognizedFromFile:
            transcribed_text = result.text
            print(f"✓ Recognition succeeded!")
            print(f"\nTranscribed Text:")
            print(f"  {transcribed_text}")
            return transcribed_text
            
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print(f"✗ No speech detected")
            print(f"  Error Details: {result.no_match_details}")
            return None
            
        elif result.reason == speechsdk.ResultReason.Canceled:
            error = result.cancellation_details
            print(f"✗ Recognition canceled")
            print(f"  Error Code: {error.error_code}")
            print(f"  Error Details: {error.error_details}")
            return None
            
    except Exception as e:
        print(f"ERROR: Failed to convert speech to text: {e}")
        return None


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Main program flow"""
    print("\n" + "="*60)
    print("Assignment 21: Recognize Speech with an IoT Device")
    print("="*60)
    
    # Task 3: Capture audio
    print("\n[1/2] Capturing audio from microphone...")
    if not capture_audio():
        print("\nFailed to capture audio. Exiting.")
        return
    
    # Task 5: Recognize speech
    print("\n[2/2] Converting speech to text...")
    text = recognize_speech()
    
    if text:
        print("\n" + "="*60)
        print("SUCCESS! ✓")
        print("="*60)
        print(f"\nFinal Result: {text}")
    else:
        print("\n" + "="*60)
        print("FAILED ✗")
        print("="*60)
        print("\nTroubleshooting:")
        print("1. Check microphone is connected and working")
        print("2. Check Azure API key in .env file")
        print("3. Verify Azure Speech Service region")
        print("4. Check internet connection")


if __name__ == "__main__":
    main()
