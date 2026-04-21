# Quick Start Setup Guide

## Option 1: Run Locally (Easiest for Testing)

### Step 1: Get a Free API Key
1. Go to https://openweathermap.org/api
2. Click "Sign Up" and create a free account
3. Go to "API keys" tab
4. Copy your default API key (it will be a long string)

### Step 2: Add API Key to Code
1. Open `app.js` in an editor
2. Find this line (near the top):
   ```javascript
   const API_KEY = 'YOUR_OPENWEATHER_API_KEY';
   ```
3. Replace `YOUR_OPENWEATHER_API_KEY` with your actual API key:
   ```javascript
   const API_KEY = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6';
   ```
4. Save the file

### Step 3: Run the App
- Just open `index.html` in your web browser
- Type a city name (e.g., "London", "Paris", "Tokyo")
- Click "Search" or press Enter
- Weather data should appear!

### Step 4: Test with Different Cities
- New York
- Tokyo
- Sydney
- Dublin

---

## Option 2: Deploy to Azure Static Web Apps

### Prerequisites
- Azure account (get free tier here: https://azure.microsoft.com/free)
- GitHub account
- This code pushed to GitHub

### Step 1: Create Azure Static Web App
1. Go to https://portal.azure.com
2. Search for "Static Web Apps" and click "Create"
3. Fill in:
   - Resource Group: create new
   - Name: `weather-app` (or your choice)
   - Region: closest to you
   - Plan: Free
4. Click "Sign in with GitHub" and authorize
5. Select:
   - Organization: yours
   - Repository: `IoT-Assignments`
   - Branch: `main`

### Step 2: Configure Build
1. Build Presets: select "Custom"
2. App location: `/Assignment_13`
3. Leave API location and output location empty
4. Click "Review + Create"
5. Click "Create" and wait 2-3 minutes

### Step 3: Add Environment Variable
1. In Azure Portal, go to your Static Web App
2. Click "Settings" > "Environment variables"
3. Click "Add"
4. Name: `WEATHER_API_KEY`
5. Value: paste your OpenWeather API key
6. Click "Save"
7. Wait for redeploy (1-2 minutes)

### Step 4: Access Your App
- Your URL will be: `https://your-app-name.azurestaticapps.net`
- Share this URL with anyone!

---

## Troubleshooting

### "City not found" error
- ✅ Check spelling (case-insensitive, so "LONDON" = "london")
- ✅ Try full name like "New York" instead of "NY"
- ✅ Add country code: "Paris, FR"

### "API key not configured" error
- ✅ You forgot to update `app.js` with your real API key
- ✅ Check you copied the API key correctly (no extra spaces)

### Nothing happens when I search
- ✅ Open your browser's Developer Tools (F12 or Ctrl+Shift+I)
- ✅ Look at "Console" tab for error messages
- ✅ Check that API key in `app.js` is valid

### App works locally but not on Azure
- ✅ Make sure you added `WEATHER_API_KEY` environment variable in Azure Portal
- ✅ Wait 2-3 minutes after adding the variable
- ✅ Hard refresh browser (Ctrl+F5)

---

## File Descriptions

| File | Purpose |
|------|---------|
| `index.html` | The user interface (HTML + CSS) |
| `app.js` | JavaScript logic (API calls, data display) |
| `.gitignore` | Tells Git to ignore sensitive files |
| `staticwebapp.config.json` | Azure configuration |
| `README.md` | Full documentation |
| `SETUP.md` | This quick start guide |

---

## Security Note

**For Local Testing:**
- ✅ OK to put API key directly in `app.js`

**For Production/Azure:**
- 🔒 DO NOT commit API key to GitHub
- 🔒 Use environment variables in Azure Portal instead
- ✅ We've done this for you - just add the variable in Azure Settings

---

## Next Steps

1. ✅ Get API key from openweathermap.org
2. ✅ Update `app.js` with your key
3. ✅ Test by opening `index.html` in browser
4. ✅ Search for cities and verify weather data works
5. ✅ (Optional) Deploy to Azure following Option 2

**Estimated time:** 5-10 minutes

Questions? Check the README.md for more details!
