from django.core.management.base import BaseCommand
from dungeons.models import WorldZone, Dungeon

class Command(BaseCommand):
    help = 'Inspect WorldZone and Dungeon data'

    def handle(self, *args, **options):
        self.stdout.write("Inspecting WorldZones and Dungeons...")
        zones = WorldZone.objects.all()
        for zone in zones:
            self.stdout.write(f"Zone: {zone.name} (ID: {zone.id})")
            dungeons = Dungeon.objects.filter(zone=zone)
            if dungeons.exists():
                for dungeon in dungeons:
                    self.stdout.write(f"  - Dungeon: {dungeon.name} (ID: {dungeon.id})")
            else:
                self.stdout.write("  No dungeons found in this zone.")
