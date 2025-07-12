
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from dungeons.models import WorldZone, PlayerGate
from dungeons.dungeon_manifest_service import DungeonManifestService
import math

class Command(BaseCommand):
    help = 'Fixes all map data by redistributing zones and regenerating player gates.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- STARTING MAP DATA REPAIR ---"))

        # 1. Wipe all existing player gates
        self.stdout.write("Deleting all existing player gates...")
        PlayerGate.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("All player gates have been deleted."))

        # 2. Intelligently redistribute zones
        self.stdout.write("Redistributing world zones...")
        zones = list(WorldZone.objects.all())
        num_zones = len(zones)

        if num_zones == 0:
            self.stdout.write(self.style.WARNING("No zones found to distribute."))
            return

        map_width = 3840
        map_height = 1800
        center_x = map_width / 2
        center_y = map_height / 2

        a = 150
        b = 120

        for i, zone in enumerate(zones):
            angle = 0.6 * i
            radius = a + b * angle
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            zone.world_map_x = int(max(150, min(x, map_width - 150)))
            zone.world_map_y = int(max(150, min(y, map_height - 150)))
            zone.save()
            self.stdout.write(f"  - Moved '{zone.name}' to (x: {zone.world_map_x}, y: {zone.world_map_y})")

        self.stdout.write(self.style.SUCCESS(f"Successfully distributed {num_zones} zones."))

        # 3. Regenerate all player gates
        self.stdout.write("Regenerating daily gates for all users...")
        User = get_user_model()
        for user in User.objects.all():
            DungeonManifestService.generate_daily_manifest(user)
            self.stdout.write(f"  - Generated gates for {user.username}")

        self.stdout.write(self.style.SUCCESS("--- MAP DATA REPAIR COMPLETE ---"))
