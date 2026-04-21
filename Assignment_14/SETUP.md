# Assignment 14: Geofence Notifications Setup Guide

## Overview

This assignment implements geofence notifications using Twilio SMS and SendGrid Email through Azure Functions. When GPS coordinates enter or exit a defined geofence, the system automatically sends a notification.

## Components

1. **index.html** - UI for testing geofence with different coordinates
2. **geofence-notify.js** - Client-side geofence detection logic
3. **notify-geofence.py** - Azure Function to send notifications via Twilio/SendGrid

## Step 1: Set Up Twilio Account

### Create Account
1. Go to https://www.twilio.com/
2. Click **Sign Up** (free trial: $15 credit)
3. Verify your email and phone number
4. Complete account setup

### Get Twilio Credentials
1. Go to Twilio Console Dashboard
2. Find your **Account SID** and **Auth Token**
3. Go to **Phone Numbers** > **Manage Numbers**
4. Set up a phone number (trial accounts have limitations)

### Get Credentials
```
- TWILIO_ACCOUNT_SID: ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
- TWILIO_AUTH_TOKEN: your_auth_token_here
- TWILIO_PHONE_NUMBER: +1234567890 (your Twilio number)
```

---

## Step 2: Set Up SendGrid Account

### Create Account
1. Go to https://sendgrid.com/
2. Click **Sign Up** (free tier: 100 emails/day)
3. Verify your email
4. Complete company info

### Get API Key
1. Go to Settings > API Keys
2. Click "Create API Key"
3. Name: "Geofence Notifications"
4. Select "Full Access"
5. Click "Create & Copy"
6. Save as **SENDGRID_API_KEY**

---

## Step 3: Create Azure Function

### Deploy Function
1. Create new **HTTP Trigger** function in VS Code or Azure Portal
2. Copy code from `notify-geofence.py` into the function
3. Set up bindings for **Twilio** or **SendGrid**

### Configure Bindings

**For Twilio SMS:**
1. In Azure Portal, go to your Function App
2. Click "Integration" on the function
3. Click "+ Add output"
4. Select "Twilio SMS"
5. Fill in:
   - Binding name: `twilioSms`
   - Twilio Account SID: [from Step 1]
   - Twilio Auth Token: [from Step 1]
6. Click "OK"

**For SendGrid Email:**
1. Click "+ Add output"
2. Select "SendGrid"
3. Fill in:
   - Binding name: `sendGrid`
   - SendGrid API Key: [from Step 2]
4. Click "OK"

### Add Application Settings
In Azure Portal > Function App > Settings > Environment Variables:
```
TWILIO_ACCOUNT_SID = ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN = your_auth_token
TWILIO_PHONE_NUMBER = +1234567890
SENDGRID_API_KEY = SG.xxxxxxxxxxxxxxxxxxxx
```

---

## Step 4: Test Geofence Notifications

### Local Testing
1. Open `index.html` in browser
2. Set geofence center (e.g., New York: 40.7128, -74.0060)
3. Set radius (e.g., 5 km)
4. Add email or phone for notifications
5. Enter GPS coordinates and click "Check Location"

### Expected Behavior
- **Inside geofence**: Shows green indicator, may trigger email/SMS
- **Outside geofence**: Shows red indicator
- **Boundary crossing**: Triggers notification (entered/exited)

---

## Step 5: Complete Azure Functions Integration

### Update notify-geofence Function

```python
import azure.functions as func
import json
import os
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

@app.route(route="notify-geofence")
def notify_geofence(req: func.HttpRequest) -> func.HttpResponse:
    req_body = req.get_json()
    event = req_body.get('event')  # 'entered' or 'exited'
    email = req_body.get('email')
    phone = req_body.get('phone')
    
    # Send EITHER email OR SMS, not both
    if email:
        send_email(email, event)
    elif phone:
        send_sms(phone, event)
    
    return func.HttpResponse(f"Notification sent: {event}", status_code=200)

def send_email(email, event):
    sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
    message = Mail(
        from_email='noreply@geofence.app',
        to_emails=email,
        subject=f'Geofence Alert: You {event}!',
        html_content=f'<p>You {event} the geofenced area</p>'
    )
    sg.send(message)

def send_sms(phone, event):
    client = Client(
        os.environ['TWILIO_ACCOUNT_SID'],
        os.environ['TWILIO_AUTH_TOKEN']
    )
    client.messages.create(
        to=phone,
        from_=os.environ['TWILIO_PHONE_NUMBER'],
        body=f'Geofence: You {event} the area!'
    )
```

---

## Testing Checklist

- [ ] Twilio account created with phone number
- [ ] SendGrid account created with API key
- [ ] Azure Function deployed with bindings
- [ ] Environment variables set in Azure
- [ ] Local HTML form shows geofence status correctly
- [ ] Email notification received when entering geofence
- [ ] SMS notification received when exiting geofence
- [ ] Only ONE notification sent (email OR SMS, not both)

---

## Rubric Checklist

**Exemplary:**
- [ ] Configured Twilio SMS OR SendGrid Email (one, not both)
- [ ] Receive notification when GPS inside geofence
- [ ] Receive notification when GPS outside geofence
- [ ] Different message for entry vs exit events

**Adequate:**
- [ ] Configured bindings but some issues sending notifications
- [ ] Notifications only work in limited scenarios

**Needs Improvement:**
- [ ] Unable to configure bindings
- [ ] No notifications sent

---

## Resources

- [Twilio Docs](https://www.twilio.com/docs)
- [SendGrid Docs](https://sendgrid.com/docs)
- [Azure Functions Twilio Binding](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-twilio)
- [Azure Functions SendGrid Binding](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-sendgrid)

---

## Troubleshooting

### No Email Received
- Check SendGrid API key in environment variables
- Verify email address is in recipient list
- Check spam folder

### No SMS Received
- Verify Twilio phone number is active
- Check destination phone number format (+1234567890)
- Trial accounts may have restrictions

### Function Error
- Check Function App logs in Azure Portal
- Verify all environment variables are set
- Test with manual API call

---

**Status**: Ready for deployment
