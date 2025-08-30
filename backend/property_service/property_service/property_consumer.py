import pika, json, os, time

RABBIT_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBIT_USER = os.getenv("RABBITMQ_DEFAULT_USER", "guest")
RABBIT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "guest")

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(" [x] Received:", data)
    # handle event: send email, store analytics, notify other service, etc.

def start_consumer():
    while True:
        try:
            creds = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
            params = pika.ConnectionParameters(host=RABBIT_HOST, credentials=creds, heartbeat=600)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            for q in ["property_created", "property_updated", "property_deleted"]:
                channel.queue_declare(queue=q, durable=True)
                channel.basic_consume(queue=q, on_message_callback=callback, auto_ack=True)
            print(" [*] Waiting for messages. To exit press CTRL+C")
            channel.start_consuming()
        except Exception as e:
            print("Consumer error:", e)
            time.sleep(5)

if __name__ == "__main__":
    start_consumer()
