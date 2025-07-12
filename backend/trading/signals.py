from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Trade
from notifications.notification_utils import notify_admins_pending_trade_approval

@receiver(post_save, sender=Trade)
def notify_admins_on_new_trade(sender, instance, created, **kwargs):
    # Notify admins only if trade requires admin approval and is pending
    if created and instance.admin_approval and instance.status == 'pending':
        notify_admins_pending_trade_approval(instance)
