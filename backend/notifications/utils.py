from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from .discord_bot import send_discord_dm

def send_user_notification(user, message, send_discord=True):
    """Saves a notification and sends it via WebSocket and optionally Discord."""
    # 1. Save to database
    Notification.objects.create(recipient=user, message=message)

    # 2. Send real-time notification via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user.id}',
        {
            'type': 'send_notification',
            'message': message
        }
    )

    # 3. Send via Discord DM
    if send_discord and user.discord_id:
        send_discord_dm(user.discord_id, message)
    
def send_group_notification(users, message, send_discord=True):
    
    for user in users:
        send_user_notification(user, message, send_discord)
