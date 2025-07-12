from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import User
from notifications.notification_utils import send_notification, notify_admins_pending_approval

@receiver(pre_save, sender=User)
def send_admin_approval_email(sender, instance, **kwargs):
    if not instance.pk:
        # New user, nothing to compare
        return
    try:
        old = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return
    # Send email only if is_approved changes from False to True
    if not old.is_approved and instance.is_approved:
        subject = 'Your Account Has Been Approved!'
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost')
        to_email = [instance.email]
        context = {'user': instance}
        html_content = render_to_string('account/email/admin_approval_message.html', context)
        text_content = 'Your account has been approved! You can now log in.'
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        # Website and Discord notification
        send_notification(instance, 'approval', 'Your account has been approved! You can now log in.')

@receiver(post_save, sender=User)
def notify_admins_on_new_user(sender, instance, created, **kwargs):
    if created and not instance.is_approved:
        notify_admins_pending_approval()
