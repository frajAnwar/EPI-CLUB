from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event, Tournament
from notifications.notification_utils import notify_admins_pending_event_approval, notify_admins_pending_tournament_approval

@receiver(post_save, sender=Event)
def notify_admins_on_new_event(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        notify_admins_pending_event_approval(instance)

@receiver(post_save, sender=Tournament)
def notify_admins_on_new_tournament(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        notify_admins_pending_tournament_approval(instance)
