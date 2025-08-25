from django.core.management.commands.runserver import Command as RunServerCommand
import threading
from booking.utilis import consumer

class Command(RunServerCommand):
    def run(self, *args, **options):
        thread = threading.Thread(target=consumer.start_consumer, daemon=True)
        thread.start()
        super().run(*args, **options)
