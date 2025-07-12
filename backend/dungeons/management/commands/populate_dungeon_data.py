from django.core.management.base import BaseCommand
from dungeons.models import Dungeon
import random

class Command(BaseCommand):
    help = 'Populates rarity drop rates and floor power levels for all dungeons'

    def handle(self, *args, **options):
        self.stdout.write('Populating dungeon data...')

        for dungeon in Dungeon.objects.all():
            # Populate rarity drop rates
            dungeon.rarity_drop_rates = {
                'common': 0.40,
                'uncommon': 0.20,
                'rare': 0.10,
                'epic': 0.05,
                'legendary': 0.01,
            }

            # Populate floor power levels
            floor_power_levels = []
            for i in range(dungeon.max_floors):
                floor_power_levels.append(dungeon.base_xp + (i * 20)) # Example calculation
            dungeon.floor_power_levels = floor_power_levels

            dungeon.save()
            self.stdout.write(f'Updated data for "{dungeon.name}"')

        self.stdout.write(self.style.SUCCESS('Successfully populated dungeon data.'))
