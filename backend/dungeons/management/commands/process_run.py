from django.core.management.base import BaseCommand
from dungeons.models import DungeonRun
from dungeons.engine import DungeonEngine

class Command(BaseCommand):
    help = 'Process a dungeon run'

    def add_arguments(self, parser):
        parser.add_argument('--run_id', type=int, help='The ID of the dungeon run to process')

    def handle(self, *args, **options):
        run_id = options['run_id']
        try:
            dungeon_run = DungeonRun.objects.get(id=run_id)
        except DungeonRun.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Dungeon run with ID {run_id} not found'))
            return

        engine = DungeonEngine(dungeon_run.user)
        engine.process_dungeon_run(dungeon_run)

        self.stdout.write(self.style.SUCCESS(f'Dungeon run {run_id} processed successfully'))
