from django.core.management.base import BaseCommand
from dungeons.models import WorldZone, Dungeon, WorldEvent, WorldEventEffect, EntityCategory, DungeonQuest
from items.models import Item, ItemCategory

class Command(BaseCommand):
    help = 'Seeds the database with initial world data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding world data...')

        # Create Item Categories
        material_category, _ = ItemCategory.objects.get_or_create(name='Material')
        consumable_category, _ = ItemCategory.objects.get_or_create(name='Consumable')

        # Create Items
        map_fragment, _ = Item.objects.get_or_create(
            name='Map Fragment',
            description='A fragment of a map that can be used to reveal hidden gates.',
            rarity='Common',
        )
        map_fragment.categories.add(consumable_category)

        # Create Entity Categories
        beast_category, _ = EntityCategory.objects.get_or_create(name='Beast')
        goblin_category, _ = EntityCategory.objects.get_or_create(name='Goblin')

        # Create World Zones
        ashwood, _ = WorldZone.objects.update_or_create(
            svg_id='zone-ashwood',
            defaults={
                'name': 'Ashwood',
                'svg_path': 'M100,100 L300,100 L300,300 L100,300 Z',
                'label_x': 150,
                'label_y': 200
            }
        )

        caldera, _ = WorldZone.objects.update_or_create(
            svg_id='zone-caldera',
            defaults={
                'name': 'Scorched Caldera',
                'svg_path': 'M400,150 L600,150 L600,350 L400,350 Z',
                'label_x': 450,
                'label_y': 250
            }
        )

        # Create Dungeons
        goblin_lair, _ = Dungeon.objects.get_or_create(
            name='Goblin Lair',
            rank='E',
            zone=ashwood,
            base_xp=50,
            base_currency=25,
            min_floors=2,
            max_floors=4,
        )
        goblin_lair.entity_categories.add(goblin_category)

        wolf_den, _ = Dungeon.objects.get_or_create(
            name='Wolf Den',
            rank='D',
            zone=ashwood,
            base_xp=100,
            base_currency=50,
            min_floors=3,
            max_floors=5,
        )
        wolf_den.entity_categories.add(beast_category)

        # Create Hidden Dungeon
        hidden_cave, _ = Dungeon.objects.get_or_create(
            name='Hidden Cave',
            rank='C',
            zone=ashwood,
            base_xp=200,
            base_currency=100,
            min_floors=5,
            max_floors=8,
        )
        hidden_cave.entity_categories.add(beast_category)
        ashwood.hidden_gates.add(hidden_cave)

        # Create World Events
        blood_moon, _ = WorldEvent.objects.update_or_create(
            identifier='blood_moon',
            defaults={
                'name': 'Blood Moon',
                'event_type': 'ENVIRONMENTAL',
                'description': 'The moon turns red, empowering beasts and increasing their spawn rate.',
                'duration_hours': 12,
                'cooldown_hours': 48,
                'map_icon': '<circle cx="0" cy="0" r="10" fill="red" />'
            }
        )
        blood_moon_effect, _ = WorldEventEffect.objects.get_or_create(
            identifier='blood_moon_effect',
            name='Beast Spawn Rate Increase',
            effect_type='SPAWN_MOD',
            parameters={'Beast': 2.0}
        )
        blood_moon.effects.add(blood_moon_effect)

        self.stdout.write(self.style.SUCCESS('Successfully seeded world data.'))
