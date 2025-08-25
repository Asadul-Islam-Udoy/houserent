import pika
import json
import time

RABBITMQ_HOST = "127.0.0.1"  # e.g., "127.0.0.1" or cloud endpoint
RABBITMQ_PORT = 5672
RABBITMQ_APIKEY = "91f553e4-b561-4340-983b-12f8cbf96f6f"   # your RabbitMQ password
ORDER_QUEUE = "order_created"
PAYMENT_QUEUE = "payment_completed"

def start_consumer():
    while True:
        try:
            credentials = pika.PlainCredentials(username="apikey", password=RABBITMQ_APIKEY)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
            )
            channel = connection.channel()
            channel.queue_declare(queue=ORDER_QUEUE, durable=True)
            print("[*] Payment service listening...")

            # Start consuming
            def process_order(ch, method, properties, body):
                data = json.loads(body.decode())
                print(f"[Payment] Received order: {data}")
                payment_status = {"order_id": data["order_id"], "status": "paid"}
                # Publish to PAYMENT_QUEUE
                channel.queue_declare(queue=PAYMENT_QUEUE, durable=True)
                channel.basic_publish(
                    exchange="",
                    routing_key=PAYMENT_QUEUE,
                    body=json.dumps(payment_status),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                print(f"[Payment] Published to {PAYMENT_QUEUE}: {payment_status}")

            channel.basic_consume(
                queue=ORDER_QUEUE,
                on_message_callback=process_order,
                auto_ack=True
            )
            channel.start_consuming()

        except Exception as e:
            print(f"[Payment] RabbitMQ connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    start_consumer()
