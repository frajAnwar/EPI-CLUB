from notifications.models import Notification
from accounts.models import User
from accounts.discord_utils import send_discord_dm
from django.contrib.auth import get_user_model

def send_notification(user, notif_type, content, extra_data=None, send_discord=True):
    notif = Notification.objects.create(recipient=user, message=content)
    # Optionally store extra_data in Notification if you extend the model
    if send_discord and getattr(user, 'discord_id', None):
        try:
            send_discord_dm(user.discord_id, content)
        except Exception:
            pass  # Fail silently for Discord errors
    return notif

def notify_admins_pending_approval():
    User = get_user_model()
    admins = User.objects.filter(is_admin=True)
    for admin in admins:
        send_notification(
            admin,
            'pending_approval',
            'A new user registration is pending approval. <a href="/admin/accounts/user/">Review now</a>'
        )

def notify_admins_pending_team_approval(team):
    User = get_user_model()
    admins = User.objects.filter(is_admin=True)
    for admin in admins:
        send_notification(
            admin,
            'pending_team_approval',
            f'Team "{team.name}" is pending approval. <a href="/admin/accounts/team/">Review now</a>'
        )

def notify_admins_pending_tournament_approval(tournament):
    User = get_user_model()
    admins = User.objects.filter(is_admin=True)
    for admin in admins:
        send_notification(
            admin,
            'pending_tournament_approval',
            f'Tournament "{tournament.name}" is pending approval. <a href="/admin/events/tournament/">Review now</a>'
        )

def notify_admins_pending_event_approval(event):
    User = get_user_model()
    admins = User.objects.filter(is_admin=True)
    for admin in admins:
        send_notification(
            admin,
            'pending_event_approval',
            f'Event "{event.name}" is pending approval. <a href="/admin/events/event/">Review now</a>'
        )

def notify_admins_pending_trade_approval(trade):
    User = get_user_model()
    admins = User.objects.filter(is_admin=True)
    for admin in admins:
        send_notification(
            admin,
            'pending_trade_approval',
            f'Trade from {trade.from_user.username} to {trade.to_user.username} for {trade.item.name} is pending approval. <a href="/admin/trading/trade/">Review now</a>'
        )
