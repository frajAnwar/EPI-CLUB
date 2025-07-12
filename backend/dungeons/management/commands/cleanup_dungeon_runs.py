from django.core.management.base import BaseCommand
from dungeons.models import DungeonRun
from accounts.models import User

class Command(BaseCommand):
    help = 'Cleans up duplicate in-progress DungeonRun objects for each user, keeping only the most recent one.'

    def handle(self, *args, **options):
        for user in User.objects.all():
            runs = DungeonRun.objects.filter(user=user, status='in_progress').order_by('-start_time')
            if runs.count() > 1:
                self.stdout.write(self.style.WARNING(f'Found {runs.count()} in-progress runs for user {user.email}. Cleaning up...'))
                # Keep the first run (the most recent one) and delete the rest
                for run_to_delete in runs[1:]:
                    run_to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f'Cleaned up runs for user {user.email}.'))
        self.stdout.write(self.style.SUCCESS('Finished cleaning up dungeon runs.'))
