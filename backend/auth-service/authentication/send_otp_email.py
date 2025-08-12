from django.conf import settings
from django.core.mail import send_mail
def send_otp_email(existing_email):
    send_mail(
        subject="Your Register OTP Code",
        message=f"Your OTP is {existing_email.otp}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[existing_email.email],
        fail_silently=False,
        )
    return True