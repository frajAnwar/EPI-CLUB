from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event, Tournament

class Command(BaseCommand):
    help = 'Update status of events and tournaments based on current time.'

    def handle(self, *args, **options):
        now = timezone.now()
        # Update Events
        for event in Event.objects.all():
            if event.status not in ['archived', 'rejected']:
                if event.start_time <= now < event.end_time:
                    if event.status != 'live':
                        event.status = 'live'
                        event.save()
                        self.stdout.write(self.style.SUCCESS(f'Event {event.name} set to live.'))
                elif now >= event.end_time:
                    if event.status != 'completed':
                        event.status = 'completed'
                        event.save()
                        self.stdout.write(self.style.SUCCESS(f'Event {event.name} set to completed.'))
                elif now < event.start_time:
                    if event.status != 'upcoming':
                        event.status = 'upcoming'
                        event.save()
                        self.stdout.write(self.style.SUCCESS(f'Event {event.name} set to upcoming.'))
        # Update Tournaments
        for tournament in Tournament.objects.all():
            if tournament.status not in ['archived', 'rejected']:
                if hasattr(tournament, 'start_date') and hasattr(tournament, 'end_date'):
                    start = timezone.make_aware(timezone.datetime.combine(tournament.start_date, timezone.datetime.min.time()))
                    end = timezone.make_aware(timezone.datetime.combine(tournament.end_date, timezone.datetime.max.time()))
                    if start <= now < end:
                        if tournament.status != 'live':
                            tournament.status = 'live'
                            tournament.save()
                            self.stdout.write(self.style.SUCCESS(f'Tournament {tournament.name} set to live.'))
                    elif now >= end:
                        if tournament.status != 'completed':
                            tournament.status = 'completed'
                            tournament.save()
                            self.stdout.write(self.style.SUCCESS(f'Tournament {tournament.name} set to completed.'))
                    elif now < start:
                        if tournament.status != 'upcoming':
                            tournament.status = 'upcoming'
                            tournament.save()
                            self.stdout.write(self.style.SUCCESS(f'Tournament {tournament.name} set to upcoming.'))
