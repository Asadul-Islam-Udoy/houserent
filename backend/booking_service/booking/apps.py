from django.apps import AppConfig
import threading
import time

class BookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking'

    def ready(self):
        from booking.utilis import consumer

        def start_consumer_with_retry():
            while True:
                try:
                    consumer.start_consumer()
                    break
                except Exception as e:
                    print(f"[Consumer] RabbitMQ connection failed: {e}. Retrying in 5 seconds...")
                    time.sleep(5)

        thread = threading.Thread(target=start_consumer_with_retry, daemon=True)
        thread.start()
