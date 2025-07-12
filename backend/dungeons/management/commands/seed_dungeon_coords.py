import random
from django.core.management.base import BaseCommand
from dungeons.models import Dungeon, WorldZone

class Command(BaseCommand):
    help = 'Seeds existing dungeons with random coordinates within their zone.'

    def handle(self, *args, **options):
        self.stdout.write('Starting to seed dungeon coordinates...')
        dungeons = Dungeon.objects.all()
        for dungeon in dungeons:
            if dungeon.zone:
                # Define a buffer to keep dungeons from spawning on the very edge of the zone
                buffer = 50
                
                # Assuming the zone background is 1920x1080
                max_x = 1920 - buffer
                max_y = 1080 - buffer

                # Generate random coordinates within the valid spawn area
                random_x = random.randint(buffer, max_x)
                random_y = random.randint(buffer, max_y)

                dungeon.zone_map_x = random_x
                dungeon.zone_map_y = random_y
                dungeon.save()

                self.stdout.write(self.style.SUCCESS(f'Successfully updated coordinates for {dungeon.name} in {dungeon.zone.name}.'))
            else:
                self.stdout.write(self.style.WARNING(f'Dungeon {dungeon.name} has no assigned zone, skipping.'))

        self.stdout.write(self.style.SUCCESS('Finished seeding dungeon coordinates.'))
