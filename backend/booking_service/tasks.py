# booking_service/tasks.py
from celery import shared_task
import requests

@shared_task
def send_booking_confirmation(user_email, booking_id):
    requests.post("http://nginx/notify/send-email/", json={
        "to": user_email,
        "subject": "Booking Confirmed",
        "message": f"Your booking {booking_id} is confirmed."
    })
