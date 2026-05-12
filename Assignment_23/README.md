# Assignment 23: Set Timer and Provide Spoken Feedback

## 📋 Overview

Build the execution and feedback components of the smart timer. This assignment brings together Assignments 21-22:
- **Input**: Recognized speech from Assignment 21
- **Processing**: NLU understanding from Assignment 22
- **Output**: Set timer on device + text-to-speech feedback

**Flow**: Speech → Text → Understanding → Timer Execution → Voice Alert

---

## 🎯 Key Components

### 1. REST API Integration
Call Assignment 22 endpoint to convert speech to timer duration:

```python
# Send to Azure Function
POST http://localhost:7071/api/text-to-timer
{"text": "set a timer for 5 minutes"}

# Receive back
{"seconds": 300, "intent": "set timer", "confidence": 0.98}
```

### 2. Text-to-Speech (TTS)
Convert confirmation/alert messages to spoken audio:

```
"Your 5 minute timer is set" → 🔊 spoken audio
"Your timer is finished" → 🔊 alert audio
```

### 3. Timer Management
- Background countdown
- Check for completion
- Clean shutdown

### 4. Audio Playback
Play TTS audio through speakers

---

## 🛠️ Setup Instructions

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment

Copy `.env.example` to `.env` and fill in:

```bash
# Azure Speech Service (from Assignment 21)
SPEECH_KEY=your_key_here
SPEECH_REGION=eastus

# Assignment 22 REST endpoint
TEXT_TO_TIMER_ENDPOINT=http://localhost:7071/api/text-to-timer

# TTS Voice
TTS_VOICE=en-US-AriaNeural
```

### Step 3: Start Assignment 22 Function

In another terminal:
```bash
cd ../Assignment_22
func start
```

Output:
```
Functions:

    text-to-timer: [GET,POST] http://localhost:7071/api/text-to-timer

For detailed output, run func with --verbose flag.
```

Keep this running!

### Step 4: Test Text-to-Speech

Simple test:
```bash
python -c "
from app import text_to_speech
text_to_speech('Hello, your timer is set')
"
```

You should hear audio through speakers.

### Step 5: Run Full Workflow

```bash
python app.py
```

Expected output:
```
============================================================
Assignment 23: Set Timer with Spoken Feedback
============================================================

Test scenario: 'set a timer for 30 seconds'

Note: Make sure Assignment 22 endpoint is running!
Expected endpoint: http://localhost:7071/api/text-to-timer

============================================================
SETTING TIMER FROM SPEECH
============================================================

1. Recognized text: 'set a timer for 30 seconds'

[1/4] Sending to language understanding...
Calling REST endpoint: http://localhost:7071/api/text-to-timer
With text: set a timer for 30 seconds
✓ Got 30 seconds from endpoint

[2/4] Timer duration: 30 seconds
Formatted duration: 30 seconds

[3/4] Playing confirmation: 'Your 30 seconds timer is set'
Converting to speech: Your 30 seconds timer is set
✓ Speech synthesis successful
[Audio plays: "Your 30 seconds timer is set"]

[4/4] Starting 30 seconds countdown...

Timer running... (Ctrl+C to cancel)
Timer '': 20s remaining
Timer '': 10s remaining
Timer finished!
Converting to speech: Your 30 seconds timer is finished
✓ Speech synthesis successful
[Audio plays: "Your 30 seconds timer is finished"]

✓ SUCCESS!
```

---

## 📊 Testing Matrix

| Scenario | Input | Expected |
|----------|-------|----------|
| Basic timer | "set timer for 5 min" | Confirms "5 minutes", waits, alerts |
| Seconds | "10 second timer" | Confirms "10 seconds", waits, alerts |
| Combined | "2 min 30 sec" | Confirms "2 minutes 30 seconds" |
| Multiple calls | Set 2 timers in sequence | Both run independently |
| Interruption | Ctrl+C during countdown | Stops cleanly |
| No response | Gibberish input | "I didn't understand" message |

---

## 🔊 Available Voices

TTS supports multiple natural-sounding neural voices. Set in `.env`:

**English (US):**
- `en-US-AriaNeural` (female, default)
- `en-US-GuyNeural` (male)

**English (UK):**
- `en-GB-LibbyNeural` (female)
- `en-GB-RyanNeural` (male)

**Other languages** - See [Language Support](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support#text-to-speech)

---

## 🚀 Advanced Features

### SSML Customization

Add emphasis, pauses, rate changes:

```xml
<speak version='1.0' xml:lang='en-US'>
    <voice name='en-US-AriaNeural'>
        Your <emphasis level="strong">5 minute</emphasis> timer
        <break time="500ms"/>
        is set.
    </voice>
</speak>
```

Modify `text_to_speech()` function to use SSML.

### Multiple Timers

Track multiple named timers:

```python
timers = {
    "cooking": SmartTimer("cooking", 600),
    "laundry": SmartTimer("laundry", 1800)
}
```

### Timer Persistence

Save timer data to file/database for recovery if device restarts.

---

## 📚 Resources

### Official Documentation
- [Text-to-Speech](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/text-to-speech)
- [SSML Markup](https://www.w3.org/TR/speech-synthesis11/)
- [Available Neural Voices](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support#text-to-speech)

### Python Threading
- [Python threading module](https://docs.python.org/3/library/threading.html)
- [Daemon threads best practices](https://stackoverflow.com/questions/190010/daemon-threads-explanation)

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| **"No audio" error** | Check speaker connection, verify SPEECH_KEY |
| **REST endpoint 404** | Ensure Assignment 22 function is running |
| **Timer doesn't countdown** | Check threading isn't blocked by main thread |
| **Voice too slow/fast** | Adjust using SSML rate: `<prosody rate="1.1">` |
| **Speech synthesis fails** | Verify SPEECH_REGION matches key region |

---

## 📝 Submission Checklist

- [ ] `.env` file configured with credentials
- [ ] TTS audio plays through speakers
- [ ] REST endpoint call works
- [ ] Timer countdown runs correctly
- [ ] Confirmation speech plays
- [ ] Alert speech plays when timer finishes
- [ ] Error handling implemented
- [ ] Code commented and clean
- [ ] Multiple timers tested
- [ ] Log output shows successful flow

---

**Due Date**: [Insert date]

Good luck! ⏱️➜🔊
