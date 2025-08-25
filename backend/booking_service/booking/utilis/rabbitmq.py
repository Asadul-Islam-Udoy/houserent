import pika, json
from django.conf import settings

RABBITMQ_HOST = getattr(settings, "RABBITMQ_HOST", "localhost")

def publish_event(queue, message: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)  # persistent messages
    )
    print(f"[x] Event sent to {queue}: {message}")
    connection.close()

def test_connection():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        connection.close()
        return True
    except Exception as e:
        print("RabbitMQ connection failed:", e)
        return False
