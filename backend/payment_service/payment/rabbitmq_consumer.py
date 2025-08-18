# payment/rabbitmq_consumer.py
import pika, json
from django.conf import settings
from .models import Payment
from .payment_methods import stripe_payment, stripe_release, stripe_refund

RABBITMQ_URL = settings.RABBITMQ_URL

def publish_event(event_type, data):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange='microservice_exchange', exchange_type='fanout')
    message = json.dumps({"event": event_type, "data": data})
    channel.basic_publish(exchange='microservice_exchange', routing_key='', body=message)
    connection.close()

def handle_booking_created(data):
    amount = data['total_price'] * 0.3  # 30% advance
    payment = Payment.objects.create(
        booking_id=data['booking_id'],
        user_id=data['user_id'],
        seller_id=data['seller_id'],
        amount=amount
    )
    intent = stripe_payment(amount, data['booking_id'])
    payment.transaction_id = intent.id
    payment.save()
    publish_event("payment_completed", {
        "booking_id": data['booking_id'],
        "user_id": data['user_id'],
        "seller_id": data['seller_id'],
        "amount": amount
    })

def handle_booking_confirmed(data):
    payment = Payment.objects.get(booking_id=data['booking_id'], status='escrow')
    stripe_release(payment.transaction_id, payment.seller_id)
    payment.status = 'released'
    payment.save()
    publish_event("payment_released", {
        "booking_id": data['booking_id'],
        "user_id": payment.user_id,
        "seller_id": payment.seller_id,
        "amount": float(payment.amount)
    })

def handle_booking_rejected(data):
    payment = Payment.objects.get(booking_id=data['booking_id'], status='escrow')
    stripe_refund(payment.transaction_id)
    payment.status = 'refunded'
    payment.save()
    publish_event("payment_refunded", {
        "booking_id": data['booking_id'],
        "user_id": payment.user_id,
        "seller_id": payment.seller_id,
        "amount": float(payment.amount)
    })

def start_consumer():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange='microservice_exchange', exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='microservice_exchange', queue=queue_name)

    def callback(ch, method, properties, body):
        message = json.loads(body)
        event = message['event']
        data = message['data']
        if event == "booking_created":
            handle_booking_created(data)
        elif event == "booking_confirmed":
            handle_booking_confirmed(data)
        elif event == "booking_rejected":
            handle_booking_rejected(data)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print("Payment Service listening...")
    channel.start_consuming()



# # payment/management/commands/start_consumer.py
# from django.core.management.base import BaseCommand
# from payment.rabbitmq_consumer import start_consumer

# class Command(BaseCommand):
#     help = "Start Payment Service RabbitMQ Consumer"

#     def handle(self, *args, **kwargs):
#         start_consumer()


# python manage.py start_consumer
