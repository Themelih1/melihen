
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BlogPost
from .views import send_newsletter

@receiver(post_save, sender=BlogPost)
def send_newsletter_on_publish(sender, instance, created, **kwargs):
    if instance.status == 'published' and not instance._state.adding:
        send_newsletter(instance)