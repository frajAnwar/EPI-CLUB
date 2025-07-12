from django.core.management.base import BaseCommand
from dungeons.models import WorldZone

class Command(BaseCommand):
    help = 'Populates map data for all zones'

    def handle(self, *args, **options):
        self.stdout.write('Populating map data for all zones...')

        zones_data = {
            'Ashwood': {'x': 200, 'y': 300, 'path': 'M100,100 h 200 v 200 h -200 Z', 'bg': '<rect x="0" y="0" width="1000" height="1000" fill="#a8d8a8" />'},
            'Scorched Caldera': {'x': 700, 'y': 600, 'path': 'M600,500 h 200 v 200 h -200 Z', 'bg': '<rect x="0" y="0" width="1000" height="1000" fill="#ffb347" />'},
            'The Frost-Fanged Peaks': {'x': 500, 'y': 100, 'path': 'M400,50 h 200 v 100 h -200 Z', 'bg': '<rect x="0" y="0" width="1000" height="1000" fill="#b0e0e6" />'},
            'The Sunken City of Eldoria': {'x': 150, 'y': 700, 'path': 'M100,650 h 100 v 100 h -100 Z', 'bg': '<rect x="0" y="0" width="1000" height="1000" fill="#4682b4" />'},
            'The Clockwork City of Chronos': {'x': 800, 'y': 200, 'path': 'M750,150 h 100 v 100 h -100 Z', 'bg': '<rect x="0" y="0" width="1000" height="1000" fill="#c0c0c0" />'},
            'The Dragon\'s Graveyard': {'x': 400, 'y': 800, 'path': 'M350,750 h 100 v 100 h -100 Z', 'bg': '<rect x="0" y="0" width="1000" height="1000" fill="#a9a9a9" />'},
            'The Void Nexus': {'x': 900, 'y': 900, 'path': 'M850,850 h 100 v 100 h -100 Z', 'bg': '<rect x="0" y="0" width="1000" height="1000" fill="#4b0082" />'},
        }

        for zone_name, data in zones_data.items():
            try:
                zone = WorldZone.objects.get(name=zone_name)
                zone.world_map_x = data['x']
                zone.world_map_y = data['y']
                zone.svg_path = data['path']
                zone.map_background = data['bg']
                zone.save()
                self.stdout.write(f'Updated map data for "{zone_name}"')
            except WorldZone.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Zone not found: {zone_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated map data for all zones.'))
