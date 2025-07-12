from django.core.management.base import BaseCommand
from dungeons.models import Dungeon, WorldZone, EntityCategory, ItemCategory

class Command(BaseCommand):
    help = 'Creates dungeons for the Scorched Caldera zone'

    def handle(self, *args, **options):
        scorched_caldera_zone, created = WorldZone.objects.get_or_create(
            name="Scorched Caldera",
            defaults={
                'description': 'A volcanic region with rivers of lava.',
                'svg_id': 'scorched-caldera',
                'svg_path': 'M300,200 L350,250 L300,300 Z',
                'label_x': 325,
                'label_y': 275,
            }
        )

        dungeons_to_create = [
            {
                "name": "Volcanic Vents",
                "rank": "C",
                "description": "A series of treacherous volcanic vents.",
                "min_floors": 5,
                "max_floors": 12,
                "base_xp": 150,
                "base_currency": 75,
            },
            {
                "name": "Lava Tubes",
                "rank": "B",
                "description": "A network of unstable lava tubes.",
                "min_floors": 8,
                "max_floors": 15,
                "base_xp": 250,
                "base_currency": 125,
            },
        ]

        for data in dungeons_to_create:
            dungeon, created = Dungeon.objects.get_or_create(
                name=data["name"],
                defaults={
                    'zone': scorched_caldera_zone,
                    'rank': data["rank"],
                    'description': data["description"],
                    'min_floors': data["min_floors"],
                    'max_floors': data["max_floors"],
                    'base_xp': data["base_xp"],
                    'base_currency': data["base_currency"],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created dungeon: {dungeon.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Dungeon already exists: {dungeon.name}'))
