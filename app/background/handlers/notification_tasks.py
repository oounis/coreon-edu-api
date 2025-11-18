from app.services.notification_service import NotificationService
from app.db.session import SessionLocal

def send_email_task(payload):
    # placeholder for real integration
    print("[TASK] Sending email:", payload)

def send_sms_task(payload):
    print("[TASK] Sending SMS:", payload)

def send_push_task(payload):
    print("[TASK] Sending push notification:", payload)
