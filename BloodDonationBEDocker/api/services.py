import requests
from django.conf import settings

def send_otp_email(to_email, otp_code):
    data = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": settings.SENDGRID_SENDER_EMAIL},
        "subject": "Your OTP Code",
        "content": [{"type": "text/html", "value": f"<strong>Your OTP code is: {otp_code}</strong>"}]
    }

    try:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            },
            json=data
        )
        print(response.status_code, response.text)
    except Exception as e:
        print("SendGrid error:", repr(e))
