from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import EventAttendance, TournamentParticipant
from notifications.models import Notification
from accounts.discord_utils import send_discord_dm

class Command(BaseCommand):
    help = 'Send reminders for upcoming events and tournaments (website + Discord)'

    def handle(self, *args, **options):
        now = timezone.now()
        # Remind for events starting in the next hour
        event_attendances = EventAttendance.objects.filter(rsvp=True, checked_in_at__isnull=True, reminder_sent=False, event__start_time__gt=now, event__start_time__lte=now + timezone.timedelta(hours=1))
        for ea in event_attendances:
            msg = f"Reminder: The event '{ea.event.name}' starts at {ea.event.start_time}. Please check in!"
            Notification.objects.create(user=ea.user, type='general', content=msg)
            if ea.user.discord_id:
                send_discord_dm(ea.user.discord_id, msg)
            ea.reminder_sent = True
            ea.save()
            self.stdout.write(self.style.SUCCESS(f"Reminder sent for event: {ea.event.name} to {ea.user.email}"))

        # Remind for tournaments starting in the next hour
        participants = TournamentParticipant.objects.filter(rsvp=True, is_checked_in=False, reminder_sent=False, tournament__start_time__gt=now, tournament__start_time__lte=now + timezone.timedelta(hours=1))
        for tp in participants:
            msg = f"Reminder: The tournament '{tp.tournament.name}' starts at {tp.tournament.start_time}. Please check in!"
            Notification.objects.create(user=tp.user, type='general', content=msg)
            if tp.user.discord_id:
                send_discord_dm(tp.user.discord_id, msg)
            tp.reminder_sent = True
            tp.save()
            self.stdout.write(self.style.SUCCESS(f"Reminder sent for tournament: {tp.tournament.name} to {tp.user.email}"))
