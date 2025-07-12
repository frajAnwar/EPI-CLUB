from django.core.management.base import BaseCommand
from accounts.models import User
from dungeons.models import DungeonRun

class Command(BaseCommand):
    help = 'Get the hunter dashboard for a specific user'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='The email of the user to get the dashboard for')

    def handle(self, *args, **options):
        email = options['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email {email} not found'))
            return

        dungeon_runs = DungeonRun.objects.filter(user=user, status='in_progress')
        self.stdout.write(self.style.SUCCESS(f'--- Hunter Dashboard for {email} ---'))
        for run in dungeon_runs:
            self.stdout.write(f'  Run ID: {run.id}')
            self.stdout.write(f'  Dungeon: {run.dungeon.name}')
            self.stdout.write(f'  Rank: {run.dungeon.rank}')
            self.stdout.write(f'  Floor: {run.current_floor}/{run.total_floors}')
            self.stdout.write(f'  Anima: {run.anima}')
            self.stdout.write('---')
