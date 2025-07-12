from django.core.management.base import BaseCommand
from dungeons.models import Dungeon, Entity, EntityCategory, WorldZone
from items.models import Item, ItemCategory

class Command(BaseCommand):
    help = 'Creates a starter E-Rank dungeon and its zone for new players.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding starter dungeon and zone...')

        # Create World Zone
        ashwood_zone, _ = WorldZone.objects.get_or_create(
            name='Ashwood',
            svg_id='zone-ashwood'
        )

        # Create Categories
        entity_cat, _ = EntityCategory.objects.get_or_create(name='Training Constructs')
        item_cat, _ = ItemCategory.objects.get_or_create(name='Training Gear')

        # Create a basic entity for the dungeon
        Entity.objects.get_or_create(
            name='Training Dummy',
            entity_type='minion',
            level=1,
            defaults={'description': 'A stationary target for practice.'}
        )[0].categories.add(entity_cat)

        # Create a basic item for the dungeon
        Item.objects.get_or_create(
            name='Wooden Sword',
            rarity='common',
            defaults={'description': 'A simple sword for training.', 'base_price': 5}
        )[0].categories.add(item_cat)

        # Create the Dungeon
        dungeon, created = Dungeon.objects.get_or_create(
            name='Training Grounds',
            rank='E',
            defaults={
                'description': 'A safe place for new hunters to learn the ropes.',
                'base_xp': 10,
                'base_currency': 5,
                'min_floors': 2,
                'max_floors': 4,
                'zone': ashwood_zone,
            }
        )

        if created:
            dungeon.item_categories.add(item_cat)
            dungeon.entity_categories.add(entity_cat)
            self.stdout.write(self.style.SUCCESS('Successfully created "Training Grounds" dungeon in Ashwood.'))
        else:
            # Ensure the dungeon is assigned to the zone even if it already exists
            if not dungeon.zone:
                dungeon.zone = ashwood_zone
                dungeon.save()
                self.stdout.write(self.style.SUCCESS('Assigned existing "Training Grounds" to Ashwood zone.'))
            else:
                self.stdout.write(self.style.WARNING('"Training Grounds" dungeon already exists and is assigned to a zone.'))
