# notification/rabbitmq_consumer.py
import pika, json
from django.conf import settings
from .notification_utils import send_email, send_push

RABBITMQ_URL = settings.RABBITMQ_URL

def handle_event(event, data):
    if event == "booking_created":
        send_email(f"user{data['user_id']}@example.com", "Booking Created", f"Your booking {data['booking_id']} is created successfully.")
        send_push(data['user_id'], f"Booking {data['booking_id']} created successfully.")

    elif event == "payment_completed":
        send_email(f"user{data['user_id']}@example.com", "Payment Completed", f"Advance payment of {data['amount']} completed.")
        send_email(f"user{data['seller_id']}@example.com", "Advance Received", f"Received advance payment {data['amount']} for booking {data['booking_id']}.")
        send_push(data['user_id'], f"Payment completed for booking {data['booking_id']}.")
        send_push(data['seller_id'], f"Advance payment received for booking {data['booking_id']}.")

    elif event == "payment_released":
        send_email(f"user{data['seller_id']}@example.com", "Payment Released", f"Full payment of {data['amount']} released to you.")
        send_push(data['seller_id'], f"Payment released for booking {data['booking_id']}.")

    elif event == "payment_refunded":
        send_email(f"user{data['user_id']}@example.com", "Payment Refunded", f"Payment of {data['amount']} refunded for booking {data['booking_id']}.")
        send_push(data['user_id'], f"Payment refunded for booking {data['booking_id']}.")

    elif event == "booking_confirmed":
        send_email(f"user{data['user_id']}@example.com", "Booking Confirmed", f"Booking {data['booking_id']} confirmed. Payment released to seller.")
        send_push(data['user_id'], f"Booking {data['booking_id']} confirmed.")

    elif event == "booking_rejected":
        send_email(f"user{data['user_id']}@example.com", "Booking Rejected", f"Booking {data['booking_id']} rejected. Payment refunded.")
        send_push(data['user_id'], f"Booking {data['booking_id']} rejected.")

def start_consumer():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange='microservice_exchange', exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='microservice_exchange', queue=queue_name)

    def callback(ch, method, properties, body):
        message = json.loads(body)
        handle_event(message['event'], message['data'])

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print("Notification Service listening for events...")
    channel.start_consuming()











# # notification/models.py
# from django.db import models

# class Notification(models.Model):
#     NOTIFICATION_TYPE = (
#         ('email', 'Email'),
#         ('push', 'Push'),
#     )
#     user_id = models.IntegerField()
#     type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)
#     title = models.CharField(max_length=255)
#     message = models.TextField()
#     status = models.CharField(max_length=20, default='pending')  # pending, sent, failed
#     created_at = models.DateTimeField(auto_now_add=True)







# # notification/management/commands/start_consumer.py
# from django.core.management.base import BaseCommand
# from notification.rabbitmq_consumer import start_consumer

# class Command(BaseCommand):
#     help = "Start Notification RabbitMQ Consumer"

#     def handle(self, *args, **kwargs):
#         start_consumer()



# python manage.py start_consumer