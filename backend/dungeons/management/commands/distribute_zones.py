
from django.core.management.base import BaseCommand
from dungeons.models import WorldZone
import math

class Command(BaseCommand):
    help = 'Automatically distributes WorldZones across the map in a spiral pattern.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Distributing world zones..."))

        zones = list(WorldZone.objects.all())
        num_zones = len(zones)

        if num_zones == 0:
            self.stdout.write(self.style.WARNING("No zones found to distribute."))
            return

        # Map dimensions (based on your 4K viewbox)
        map_width = 3840
        map_height = 1800
        center_x = map_width / 2
        center_y = map_height / 2

        # Spiral parameters
        a = 50  # Controls the distance between arms of the spiral
        b = 100 # Controls the tightness of the spiral

        for i, zone in enumerate(zones):
            angle = 0.5 * i
            radius = a + b * angle
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # Ensure coordinates are within map bounds
            zone.world_map_x = int(max(100, min(x, map_width - 100)))
            zone.world_map_y = int(max(100, min(y, map_height - 100)))
            zone.save()

            self.stdout.write(f"  - Moved '{zone.name}' to (x: {zone.world_map_x}, y: {zone.world_map_y})")

        self.stdout.write(self.style.SUCCESS(f"Successfully distributed {num_zones} zones."))
