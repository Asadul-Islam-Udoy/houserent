from celery import shared_task
from .models import Property
from .utils.rabbitmq import publish_message

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_property_created(self, property_id):
    try:
        prop = Property.objects.get(pk=property_id)
        publish_message("property_created", {
            "id": prop.id,
            "title": prop.title,
            "price": str(prop.price),
            "location": prop.location
        })
        return {"id": prop.id}
    except Property.DoesNotExist as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_property_updated(self, property_id):
    try:
        prop = Property.objects.get(pk=property_id)
        publish_message("property_updated", {
            "id": prop.id,
            "title": prop.title,
            "price": str(prop.price),
            "location": prop.location
        })
        return {"id": prop.id}
    except Property.DoesNotExist as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_property_deleted(self, property_id):
    publish_message("property_deleted", {"id": property_id})
    return {"id": property_id}
