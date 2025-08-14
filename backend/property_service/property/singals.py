# property/signals.py
import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import PropertyImage

@receiver(pre_delete, sender=PropertyImage)
def delete_image_file(sender, instance, **kwargs):
    """
    Delete the actual file from media/properties/ when a PropertyImage is deleted
    """
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)
