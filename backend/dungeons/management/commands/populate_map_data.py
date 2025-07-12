from django.core.management.base import BaseCommand
from dungeons.models import WorldZone, Dungeon

class Command(BaseCommand):
    help = 'Populates the database with map data for zones and dungeons'

    def handle(self, *args, **options):
        # Ashwood Zone
        ashwood_zone, _ = WorldZone.objects.get_or_create(name='Ashwood')
        ashwood_zone.world_map_x = 200
        ashwood_zone.world_map_y = 300
        ashwood_zone.map_background = '<rect x="0" y="0" width="1000" height="1000" fill="#a8d8a8" />'
        ashwood_zone.save()

        dungeons_data = [
            {'name': 'Training Grounds', 'x': 150, 'y': 200},
            {'name': 'Goblin Lair', 'x': 300, 'y': 400},
            {'name': 'Wolf Den', 'x': 500, 'y': 250},
            {'name': 'Hidden Cave', 'x': 650, 'y': 500},
        ]
        for data in dungeons_data:
            dungeon, _ = Dungeon.objects.get_or_create(name=data['name'], zone=ashwood_zone)
            dungeon.zone_map_x = data['x']
            dungeon.zone_map_y = data['y']
            dungeon.save()

        # Scorched Caldera Zone
        scorched_caldera_zone, _ = WorldZone.objects.get_or_create(name='Scorched Caldera')
        scorched_caldera_zone.world_map_x = 700
        scorched_caldera_zone.world_map_y = 600
        scorched_caldera_zone.map_background = '<rect x="0" y="0" width="1000" height="1000" fill="#ffb347" />'
        scorched_caldera_zone.save()

        dungeons_data = [
            {'name': 'Volcanic Vents', 'x': 250, 'y': 350},
            {'name': 'Lava Tubes', 'x': 550, 'y': 650},
        ]
        for data in dungeons_data:
            dungeon, _ = Dungeon.objects.get_or_create(name=data['name'], zone=scorched_caldera_zone)
            dungeon.zone_map_x = data['x']
            dungeon.zone_map_y = data['y']
            dungeon.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated map data.'))
