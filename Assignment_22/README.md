# Assignment 22: Understand Language (NLU)

## 📋 Overview

This assignment teaches Natural Language Understanding (NLU) using Microsoft LUIS. You'll build a language model that can interpret user requests to set timers in multiple ways, then extract the time duration and units.

**Previous assignment**: Assignment 21 converted speech to text
**This assignment**: Extract meaning from text using AI
**Next assignment**: Assignment 23 sets the actual timer

---

## 🎯 Key Concepts

### NLU vs Speech Recognition
| Aspect | Speech Recognition | NLU |
|--------|-------------------|-----|
| Input | Audio | Text |
| Output | Text | Meaning (intent + entities) |
| Example | "set a timer for 5 minutes" | Intent: `set_timer`, Duration: 5 min |

### Intents
**What the user wants to do**
- "set a timer"
- "cancel timer"
- "check timer status"

### Entities
**Specific information about the intent**
- Time amount: 5, "five", 1.5
- Time unit: minute, second, "mins", "secs"
- Timer name: "laundry", "cooking"

---

## 🛠️ Setup Instructions

### Step 1: Prerequisites
- Azure account
- Azure CLI installed
- Python 3.9+
- Virtual environment

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Create LUIS Authoring Resource
```bash
# Create resource group
az group create --name smart-timer --location eastus

# Create LUIS Authoring resource (Free tier)
az cognitiveservices account create \
    --name smart-timer-luis-authoring \
    --resource-group smart-timer \
    --kind LUIS.Authoring \
    --sku F0 \
    --yes \
    --location eastus

# Get authoring key
az cognitiveservices account keys list \
    --name smart-timer-luis-authoring \
    --resource-group smart-timer
```

⚠️ **Note**: LUIS is not available in all regions. If you get an error, try:
- westus, westus2
- eastus, eastus2  
- northeurope, westeurope
- southeastasia, eastasia

### Step 4: Create LUIS App via Portal

1. Go to [luis.ai](https://luis.ai)
2. Sign in with your Azure account
3. Select your authoring resource
4. Create new app: `smart-timer`
5. Culture: English (or your language)

### Step 5: Add Entities

**Add prebuilt entity:**
1. Go to **Entities** tab
2. Click **Add prebuilt entity**
3. Select **number**

**Add list entity:**
1. Click **Create**
2. Name: `time unit`
3. Type: **List**
4. Add values:
   | Normalized | Synonyms |
   |------------|----------|
   | minute | minute, minutes, min, mins |
   | second | second, seconds, sec, secs |

### Step 6: Add Intents

1. Go to **Intents** tab
2. Create new intent: `set timer`
3. Add example utterances (15+ variations):

```
set a 1 second timer
set a 4 minute timer
set a timer for 1 minute and 12 seconds
set a timer for 3 minutes
set a 9 minute 30 second timer
set timer for five minutes
I want to set a three minute timer
can you set a timer for 2 minutes
set a timer
timer for 10 minutes
5 minute timer
one minute and thirty seconds
set the timer to 2 minutes
please set a 7 minute timer
timer for 1 min 30 sec
```

LUIS will automatically highlight and link entities in your examples.

### Step 7: Train & Publish

1. Click **Train** button (wait for completion)
2. Click **Test** to validate
3. Try phrases like: `set a timer for 45 minutes and 12 seconds`
4. Click **Inspect** to see extracted entities
5. Click **Publish** → Select "Staging slot" → Done

### Step 8: Get LUIS Credentials

From LUIS Portal **Manage** tab:

**From Settings:**
- Copy your **App ID**

**From Azure Resources:**
- Select "Authoring Resource"
- Copy **Endpoint URL** (e.g., `https://eastus.api.cognitive.microsoft.com/`)
- Copy **Primary Key**

### Step 9: Create Azure Functions App

```bash
# Create Functions app
func new --template "HTTP trigger" --name smart-timer-func

# Or create full project
func init smart-timer-func --python
cd smart-timer-func
func new --template "HTTP trigger" --name text-to-timer
```

### Step 10: Configure and Test

1. Copy `.env.example` to `.env`
2. Fill in LUIS credentials
3. Copy `app.py` code to your function
4. Test locally:

```bash
func start
```

Test with curl:
```bash
curl --request POST \
  'http://localhost:7071/api/text-to-timer' \
  --header 'Content-Type: application/json' \
  --data '{"text":"set a timer for 2 minutes and 30 seconds"}'
```

Expected response:
```json
{
  "seconds": 150,
  "intent": "set timer",
  "confidence": 0.98
}
```

---

## 📊 Testing Checklist

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| Simple minute | "set a 5 minute timer" | 300 seconds |
| Seconds | "10 second timer" | 10 seconds |
| Combined | "2 min 30 sec" | 150 seconds |
| Words | "five minutes" | 300 seconds |
| Different phrasing | "timer for 3 minutes" | 180 seconds |
| Unrecognized | "what time is it" | HTTP 404 |

---

## 🚀 Deployment (Optional)

Deploy to Azure:
```bash
func azure functionapp publish smart-timer-trigger

# Get function key
az functionapp keys list \
  --resource-group smart-timer \
  --name smart-timer-trigger
```

Final endpoint:
```
https://smart-timer-trigger.azurewebsites.net/api/text-to-timer?code=YOUR_KEY
```

---

## 📚 Resources

- [LUIS Documentation](https://docs.microsoft.com/azure/cognitive-services/luis/)
- [LUIS Best Practices](https://docs.microsoft.com/azure/cognitive-services/luis/luis-concept-best-practices)
- [Azure Functions Python](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)

---

## 📝 Submission

Submit:
1. Screenshots of LUIS training examples
2. Test results showing entity extraction
3. Curl command output
4. `.env` file (optional, for reference)
5. Brief explanation of LUIS model accuracy

---

Good luck! 🧠➜🎯
