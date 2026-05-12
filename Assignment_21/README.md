# Assignment 21: Recognize Speech with an IoT Device

> Part of Microsoft IoT for Beginners - Lesson 21: Speech Recognition

## 📋 Overview

This project captures audio from a microphone and uses Azure Cognitive Services to convert speech to text. This is the foundation for building a smart kitchen timer with voice control.

### What You'll Learn

- 🎤 Configuring microphone and speaker hardware
- 🔊 Capturing audio in WAV format (16kHz, 16-bit PCM)
- 🧠 Using AI to convert speech to text
- ☁️ Integrating with Azure Cognitive Services
- 🔐 Understanding privacy implications of voice recording

---

## 🛠️ Setup Instructions

### Step 1: Clone or Navigate to This Project

```bash
cd Assignment_21
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**For Raspberry Pi**, you may also need system packages:
```bash
sudo apt-get install portaudio19-dev
sudo apt-get install libatlas-base-dev libjasper-dev libtiff5 libjasper1 libharfbuzz0b libwebp6
```

### Step 4: Set Up Azure Speech Service

#### Option A: Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name smart-timer --location eastus

# Create Speech Services resource (Free tier)
az cognitiveservices account create \
    --name smart-timer \
    --resource-group smart-timer \
    --kind SpeechServices \
    --sku F0 \
    --yes \
    --location eastus

# Get API key
az cognitiveservices account keys list \
    --name smart-timer \
    --resource-group smart-timer
```

#### Option B: Using Azure Portal

1. Go to https://portal.azure.com
2. Create a new resource: **Cognitive Services > Speech**
3. Configure:
   - Resource Group: `smart-timer`
   - Region: `eastus` (or your preferred region)
   - Pricing tier: `Free (F0)`
4. Copy the API Key from Keys & Endpoint

### Step 5: Create `.env` File

```bash
# Copy the template
cp .env.example .env

# Edit .env with your Azure credentials
# Linux/macOS:
nano .env

# Windows:
notepad .env
```

Add your Azure credentials:
```
SPEECH_KEY=your_api_key_here
SPEECH_REGION=eastus
```

⚠️ **IMPORTANT**: Never commit `.env` file! It's listed in `.gitignore`

---

## 🎙️ Microphone Setup

### For Laptop/Desktop
1. Connect USB microphone
2. Set as default input device in system settings
3. Test: `python app.py` should detect your microphone

### For Raspberry Pi
1. Connect USB microphone to Raspberry Pi
2. List devices: `arecord -l`
3. Update `SAMPLE_RATE` in `app.py` if needed

### For Wio Terminal
Refer to [Wio Terminal Audio Setup Guide](https://wiki.seeedstudio.com/Wio-Terminal-Getting-Started/)

---

## ▶️ Running the Program

### Basic Usage

```bash
python app.py
```

### Expected Output

```
============================================================
Assignment 21: Recognize Speech with an IoT Device
============================================================

============================================================
TASK 2: Setting Up Microphone & Speakers
============================================================

Found 5 audio devices:
[0] Microphone (Realtek High Definition Audio)
[1] Speakers (Realtek High Definition Audio)
[2] HDMI Output
[3] Default Audio Input
[4] Default Audio Output

Default Microphone: [0] Microphone (Realtek High Definition Audio)
Default Speaker:   [1] Speakers (Realtek High Definition Audio)

============================================================
TASK 3: Capturing Audio from Microphone
============================================================

Recording 5 seconds of audio...
Sample Rate: 16000 Hz
Channels: 1
Format: 16-bit
Output: recorded_audio.wav
--------------------------------------------------------------
Recording: [██████████████████████████████] 100%
✓ Recording complete!
✓ Saved to: recorded_audio.wav (160.2 KB)

============================================================
TASK 4 & 5: Converting Speech to Text
============================================================

Azure Speech Configuration:
  Region: eastus
  API Key: XXXXXXXX...****
  Audio File: recorded_audio.wav
--------------------------------------------------------------

Processing audio...
--------------------------------------------------------------
✓ Recognition succeeded!

Transcribed Text:
  Hello, this is a test of the speech recognition system.

============================================================
SUCCESS! ✓
============================================================

Final Result: Hello, this is a test of the speech recognition system.
```

---

## 📁 Project Structure

```
Assignment_21/
├── app.py                      # Main program
├── requirements.txt            # Python dependencies
├── .env.example               # Template for credentials
├── README.md                  # This file
├── recorded_audio.wav         # Output audio file (created after running)
└── assignment21.md            # Assignment requirements
```

---

## 🔍 Troubleshooting

### Issue: Microphone Not Found

```
ERROR: Failed to setup microphone
```

**Solution:**
```bash
# List available microphones
python -c "import pyaudio; p = pyaudio.PyAudio(); print([p.get_device_info_by_index(i)['name'] for i in range(p.get_device_count())])"

# For Raspberry Pi
arecord -l
pactl list sources
```

### Issue: No Audio Captured

```
ERROR: Failed to capture audio
```

**Possible causes:**
- Microphone disconnected
- Wrong permissions on Linux: `sudo usermod -a -G audio $USER`
- Audio levels too low: adjust in system settings
- Driver issues: update audio drivers

### Issue: Azure API Fails

```
ERROR: Failed to convert speech to text
Error Code: 403
```

**Solutions:**
- Check `.env` file has correct `SPEECH_KEY` and `SPEECH_REGION`
- Verify Azure subscription is active
- Check free tier quota isn't exceeded
- Ensure region matches resource location

### Issue: "No speech detected"

```
✗ No speech detected
```

**Solutions:**
- Speak clearly into microphone
- Reduce background noise
- Move closer to microphone
- Increase `AUDIO_DURATION` to 10 seconds
- Check microphone volume levels

### Issue: ImportError on Raspberry Pi

```
ERROR: No module named 'pyaudio'
```

**Solution:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

---

## 📊 Testing Results

### Test Case 1: English Speech Recognition ✓

**Input:** "Set a timer for five minutes"
**Output:** "Set a timer for five minutes"
**Status:** ✓ PASSED

### Test Case 2: Noisy Environment ✓

**Input:** "Ten minute timer" (with background noise)
**Output:** "Ten minute timer"
**Status:** ✓ PASSED (Note: Some words may be misrecognized in very noisy environments)

### Test Case 3: Multiple Speakers

**Input:** Two people speaking (expected to fail)
**Output:** Transcribed text from dominant speaker
**Status:** ⚠️ PARTIAL (Works for single speaker)

---

## 🎓 Concepts Used

### PCM (Pulse Code Modulation)
- Sampling rate: 16 kHz (16,000 samples/second)
- Bit depth: 16-bit (2 bytes per sample)
- Data size: 16,000 × 2 = 32 KB per second

### Azure Speech Service
- Cloud-based speech-to-text API
- Supports 100+ languages
- Free tier: 5 audio minutes/month

### Speech Recognition Model
- RNN (Recurrent Neural Network) based
- Understands context for accurate transcription
- Example: "to", "two", "too" - context determines correct spelling

---

## 📚 Additional Resources

### Official Docs
- [Azure Speech Service Documentation](https://docs.microsoft.com/azure/cognitive-services/speech-service/)
- [Azure Speech SDK for Python](https://docs.microsoft.com/python/api/overview/azure/cognitiveservices-speech-readme)

### Tutorials
- [Getting Started with Azure Speech](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/quickstarts/setup-platform?tabs=linux%2Cubuntu%2Cdotnetcli&pivots=programming-language-python)
- [Speech Recognition Basics](https://www.youtube.com/watch?v=iW0Fw0l3mrA)

### Related Lessons
- **Lesson 22**: Understand Language (Natural Language Understanding)
- **Lesson 23**: Set Timer and Provide Spoken Feedback
- **Lesson 24**: Support Multiple Languages

---

## ✅ Submission Checklist

- [ ] `app.py` runs without errors
- [ ] Audio captured successfully
- [ ] Speech recognized and converted to text
- [ ] `.env` file created (but NOT committed)
- [ ] `requirements.txt` complete
- [ ] Code is commented and well-organized
- [ ] README.md filled with your results
- [ ] Sample output included
- [ ] No API keys in committed code

---

## 📝 Notes

- **Free Tier Limit**: 5 audio minutes per month (enough for testing)
- **Sample Rate**: 16 kHz is optimal for speech (lower = faster, less accurate; higher = slower, slightly better)
- **Language**: Default is English. Azure supports 100+ languages
- **Privacy**: Audio is sent to Azure cloud for processing (consider privacy implications)

---

## 🤝 Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Review [Azure Speech Service FAQs](https://docs.microsoft.com/azure/cognitive-services/speech-service/faq-stt)
3. Post in the course discussion forum
4. Contact your instructor during office hours

---

**Good luck! 🎤➜📝**

Last Updated: 2024
Assignment: Lesson 21 - Recognize Speech with an IoT Device
