# Assignment 24: Support Multiple Languages

## 📋 Overview

Complete the smart timer project with full multilingual support. Users worldwide can interact with your device in their native language.

**Workflow**:
```
User (French):  "Mettre un minuteur pour 5 minutes"
       ↓
Translator:     "Set a timer for 5 minutes"
       ↓
NLU (English):  Parse timer request → 300 seconds
       ↓
Translator:     "Votre minuteur est réglé sur 5 minutes"
       ↓
Speaker:        🔊 French voice output
```

---

## 🌍 Supported Languages

- 🇬🇧 English (en)
- 🇪🇸 Spanish (es)
- 🇫🇷 French (fr)
- 🇩🇪 German (de)
- 🇮🇹 Italian (it)
- 🇵🇹 Portuguese (pt)
- 🇨🇳 Chinese (zh-Hans)
- 🇯🇵 Japanese (ja)
- 🇰🇷 Korean (ko)
- 🇸🇦 Arabic (ar)
- 🇮🇳 Hindi (hi)
- And 50+ more!

---

## 🛠️ Setup Instructions

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create Translator Service

```bash
# Create Translator resource
az cognitiveservices account create \
    --name smart-timer-translator \
    --resource-group smart-timer \
    --kind TextTranslation \
    --sku F0 \
    --yes \
    --location eastus

# Get API key
az cognitiveservices account keys list \
    --name smart-timer-translator \
    --resource-group smart-timer
```

### Step 3: Configure Environment

Copy `.env.example` to `.env`:

```bash
# Azure Translator
TRANSLATOR_KEY=your_key_here
TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com
TRANSLATOR_REGION=eastus

# Azure Speech (for TTS)
SPEECH_KEY=your_speech_key_here
SPEECH_REGION=eastus

# Assignment 22 endpoint
TEXT_TO_TIMER_ENDPOINT=http://localhost:7071/api/text-to-timer
```

### Step 4: Run Tests

```bash
python app.py
```

Expected output:
```
Assignment 24: Support Multiple Languages
============================================================

Supported languages:
  en: English
  es: Spanish
  fr: French
  ...

Running tests...

############################################################
Test 1: English
############################################################

============================================================
MULTILINGUAL SMART TIMER
============================================================

[1/6] Detecting language...
✓ Language: English (en)

[2/6] Translating from English to English...
✓ English text: 'set a timer for 5 minutes'

[3/6] Processing timer request...
✓ Timer duration: 300 seconds

[4/6] Formatting confirmation message...
English message: 'Your 5 minutes timer is set'

[5/6] Translating response to English...
✓ Message in English: 'Your 5 minutes timer is set'

[6/6] Speaking confirmation...
✓ TTS voice: en-US-AriaNeural

============================================================
COMPLETE WORKFLOW:
  Input (English): set a timer for 5 minutes
  → English (processing): set a timer for 5 minutes
  → Timer: 300 seconds
  → Response (English): Your 5 minutes timer is set
  → Voice: en-US-AriaNeural
============================================================
✓ Test 1 passed
```

---

## 📊 Language Code Reference

| Language | Code | TTS Voice |
|----------|------|-----------|
| English | en | en-US-AriaNeural |
| Spanish | es | es-ES-ConchitaNeural |
| French | fr | fr-FR-DeniseNeural |
| German | de | de-DE-SeraphinaNeural |
| Italian | it | it-IT-IsabellaNeural |
| Portuguese | pt | pt-BR-ThalitaNeural |
| Chinese (Simplified) | zh-Hans | zh-CN-XiaoxiaoNeural |
| Japanese | ja | ja-JP-NanamisNeural |
| Korean | ko | ko-KR-SunHiNeural |
| Arabic | ar | ar-SA-ZariyahNeural |

See [full list](https://docs.microsoft.com/en-us/azure/cognitive-services/translator/language-support) for more languages.

---

## 🚀 Advanced Features

### Auto Language Detection

```python
# Detect automatically
language = detect_language(user_input)

# Or specify manually
language = "fr"  # French
```

### Translate Any Text

```python
result = translate_text(
    text="Hello world",
    source_lang="en",
    target_lang="es"  # Spanish
)
# Result: "Hola mundo"
```

### Voice Selection by Language

```python
voice = get_voice_for_language("fr")
# Returns: "fr-FR-DeniseNeural"
```

---

## 🔄 Translation Pipeline Details

### Step-by-step Example (French User)

```
1. User input (French):
   "Mettre un minuteur pour cinq minutes"

2. Language detection:
   Detected: "fr" (French)

3. Translate to English:
   "Set a timer for five minutes"

4. Process in NLU (Assignment 22):
   Intent: "set timer"
   Duration: 300 seconds

5. Generate English response:
   "Your 5 minute timer is set"

6. Translate back to French:
   "Votre minuteur de 5 minutes est défini"

7. Select French TTS voice:
   "fr-FR-DeniseNeural"

8. Speak with French voice:
   🔊 "Votre minuteur de 5 minutes est défini"
```

---

## 📚 Translation Service Details

### Azure Translator Features
- 100+ supported languages
- Text translation
- Document translation
- Transliteration
- Profanity filtering

### Supported Language Pairs
Can translate from/to any combination of supported languages.

### API Limits
- Free tier: 2 million characters/month
- Latency: ~200-500ms per request

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| **Translation inaccurate** | Provide more context, use longer sentences |
| **Language not supported** | Check language code, use available alternatives |
| **TTS voice unavailable** | Select different language/region |
| **API 403** | Verify API key and region match |
| **Timeout** | Add retry logic, increase timeout |

---

## 🧪 Test Cases

| Scenario | Input | Expected |
|----------|-------|----------|
| English | "set timer for 5 minutes" | Process in English |
| French | "mettre minuteur 5 minutes" | Translate to English, process, translate back |
| Spanish | "temporizador 10 minutos" | Same workflow |
| Chinese | "设置5分钟计时器" | Full multilingual pipeline |

---

## 📝 Submission Checklist

- [ ] Translator service created
- [ ] Language detection working
- [ ] Translation to English working
- [ ] Translation back to user language working
- [ ] TTS voice adapts to language
- [ ] Full workflow tested with 3+ languages
- [ ] Error handling implemented
- [ ] Code commented and clean
- [ ] No credentials in code
- [ ] Performance acceptable

---

## 🎉 Congratulations!

You've completed the full IoT Smart Timer project:
- ✅ Assignment 21: Speech Recognition
- ✅ Assignment 22: Language Understanding (NLU)
- ✅ Assignment 23: Text-to-Speech & Timers
- ✅ Assignment 24: Multilingual Support

**What you learned:**
- Speech processing with AI
- Natural Language Understanding
- Cloud service integration
- Multilingual application design
- IoT device programming

---

**Due Date**: [Insert date]

Great job completing the IoT for Beginners course! 🌍✨
