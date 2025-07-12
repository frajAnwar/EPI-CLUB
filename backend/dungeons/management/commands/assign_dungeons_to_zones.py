from django.core.management.base import BaseCommand
from dungeons.models import Dungeon, WorldZone

class Command(BaseCommand):
    help = 'Assigns dungeons to zones'

    def handle(self, *args, **options):
        self.stdout.write('Assigning dungeons to zones...')

        zone_dungeons = {
            'Ashwood': [
                'E-Rank Whispering Forest',
                'E-Rank Fetid Bog',
            ],
            'Scorched Caldera': [
                'B-Rank Volcanic Lair',
                'S-Rank Demon King\'s Citadel',
            ],
            'The Frost-Fanged Peaks': [
                'D-Rank Gloomy Caverns',
                'C-Rank Glimmer-Vein Caverns',
            ],
            'The Sunken City of Eldoria': [
                'D-Rank Sunken Crypt',
                'A-Rank Abyssal Trench',
            ],
            'The Clockwork City of Chronos': [
                'C-Rank Clockwork Foundry',
                'B-Rank Sky-High Aviary',
            ],
            'The Dragon\'s Graveyard': [
                'S-Rank Dragon\'s Graveyard',
                'A-Rank Astral Prison',
            ],
            'The Void Nexus': [
                'SS-Rank Void Nexus',
                'SSS-Rank World Tree',
                'National-Rank Dimensional Rift',
            ]
        }

        for zone_name, dungeon_names in zone_dungeons.items():
            zone, created = WorldZone.objects.get_or_create(
                name=zone_name,
                defaults={'svg_id': zone_name.lower().replace(' ', '-')}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created zone: {zone_name}'))

            for dungeon_name in dungeon_names:
                try:
                    dungeon = Dungeon.objects.get(name=dungeon_name)
                    dungeon.zone = zone
                    dungeon.save()
                    self.stdout.write(f'Assigned "{dungeon_name}" to "{zone_name}"')
                except Dungeon.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Dungeon not found: {dungeon_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully assigned dungeons to zones.'))
