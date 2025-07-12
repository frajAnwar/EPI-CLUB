from django.core.management.base import BaseCommand
from dungeons.models import Dungeon, WorldZone

class Command(BaseCommand):
    help = 'Create a new dungeon'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='The name of the dungeon')
        parser.add_argument('--rank', type=str, help='The rank of the dungeon')

    def handle(self, *args, **options):
        name = options['name']
        rank = options['rank']

        if not name or not rank:
            self.stdout.write(self.style.ERROR('Please provide a name and rank for the dungeon'))
            return

        zone, _ = WorldZone.objects.get_or_create(name="Test Zone")
        dungeon = Dungeon.objects.create(name=name, rank=rank, zone=zone)
        self.stdout.write(self.style.SUCCESS(f'Dungeon "{dungeon.name}" in zone "{zone.name}" created successfully'))
