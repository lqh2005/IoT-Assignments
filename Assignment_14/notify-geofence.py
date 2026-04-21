import azure.functions as func
import json
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to send geofence notifications via Twilio SMS or SendGrid Email
    
    Expected request body:
    {
        "event": "entered" or "exited",
        "email": "recipient@example.com",
        "phone": "+1234567890",
        "latitude": 40.7580,
        "longitude": -73.9855
    }
    """
    
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid request body",
            status_code=400
        )
    
    event = req_body.get('event')
    email = req_body.get('email')
    phone = req_body.get('phone')
    
    if not event:
        return func.HttpResponse(
            "Missing 'event' field",
            status_code=400
        )
    
    # Only send ONE notification - either email OR SMS, not both
    notification_sent = False
    
    # Send Email via SendGrid
    if email:
        try:
            send_email_notification(email, event)
            notification_sent = True
        except Exception as e:
            return func.HttpResponse(
                f"Email error: {str(e)}",
                status_code=500
            )
    
    # Send SMS via Twilio (only if email not sent)
    elif phone:
        try:
            send_sms_notification(phone, event)
            notification_sent = True
        except Exception as e:
            return func.HttpResponse(
                f"SMS error: {str(e)}",
                status_code=500
            )
    
    if not notification_sent:
        return func.HttpResponse(
            "No notification method provided",
            status_code=400
        )
    
    return func.HttpResponse(
        f"Notification sent for event: {event}",
        status_code=200
    )


def send_email_notification(email: str, event: str):
    """Send email notification via SendGrid"""
    
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    
    subject = f"Geofence Alert: You {event} the zone!"
    message_body = (
        f"<strong>Geofence Notification</strong><br>"
        f"<p>You have {event} the geofenced zone.</p>"
        f"<p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
    )
    
    message = Mail(
        from_email='noreply@geofence-app.com',
        to_emails=email,
        subject=subject,
        html_content=message_body
    )
    
    sg.send(message)


def send_sms_notification(phone: str, event: str):
    """Send SMS notification via Twilio"""
    
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
    
    client = Client(account_sid, auth_token)
    
    message_body = f"Geofence Alert: You {event} the zone!"
    
    message = client.messages.create(
        body=message_body,
        from_=twilio_phone,
        to=phone
    )
