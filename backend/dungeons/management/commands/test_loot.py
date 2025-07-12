
from django.core.management.base import BaseCommand, CommandError
from dungeons.models import Entity
from dungeons.loot_services import LootService
import json

class Command(BaseCommand):
    help = 'Test the loot generation for a specific entity.'

    def add_arguments(self, parser):
        parser.add_argument('entity_id', type=int, help='The ID of the entity to test loot generation for.')
        parser.add_argument(
            '--runs',
            type=int,
            default=1,
            help='The number of times to run the loot generation test.',
        )

    def handle(self, *args, **options):
        entity_id = options['entity_id']
        num_runs = options['runs']

        try:
            entity = Entity.objects.get(id=entity_id)
        except Entity.DoesNotExist:
            raise CommandError(f'Entity with ID "{entity_id}" does not exist.')

        self.stdout.write(self.style.SUCCESS(f'Testing loot generation for: {entity.name} ({entity.rank}-Rank)'))
        self.stdout.write(self.style.SUCCESS(f'Running test {num_runs} time(s)...\n'))

        total_items = {}

        for i in range(num_runs):
            loot = LootService.generate_loot(entity)
            self.stdout.write(f"--- Run {i + 1} ---")
            self.stdout.write(f"  XP: {loot['xp']}")
            self.stdout.write(f"  Coins: {loot['coins']}")
            if loot['items']:
                for item in loot['items']:
                    item_id = item['item_id']
                    total_items[item_id] = total_items.get(item_id, 0) + 1
                    self.stdout.write(self.style.WARNING(f"  Item Drop: ID {item_id}"))
            else:
                self.stdout.write("  No items dropped.")
            self.stdout.write("\n")

        if num_runs > 1:
            self.stdout.write(self.style.SUCCESS("--- Summary ---"))
            self.stdout.write("Total Item Drops:")
            for item_id, count in total_items.items():
                self.stdout.write(f"  Item ID {item_id}: {count} time(s)")
