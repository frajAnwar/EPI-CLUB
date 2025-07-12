from django.core.management.base import BaseCommand
from dungeons.models import PlayerDungeonState
from accounts.models import User

class Command(BaseCommand):
    help = 'Cleans up duplicate PlayerDungeonState objects for each user, keeping only the most recent one.'

    def handle(self, *args, **options):
        for user in User.objects.all():
            states = PlayerDungeonState.objects.filter(user=user).order_by('-last_found')
            if states.count() > 1:
                self.stdout.write(self.style.WARNING(f'Found {states.count()} states for user {user.email}. Cleaning up...'))
                # Keep the first state (the most recent one) and delete the rest
                for state_to_delete in states[1:]:
                    state_to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f'Cleaned up states for user {user.email}.'))
        self.stdout.write(self.style.SUCCESS('Finished cleaning up dungeon states.'))
