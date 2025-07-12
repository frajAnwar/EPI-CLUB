
from django.core.management.base import BaseCommand
from dungeons.models import Entity, EntityCategory
from items.models import ItemCategory

class Command(BaseCommand):
    help = 'Seeds the database with loot tables for existing entities based on their category.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Starting Loot Table Seeding Process ---'))

        # --- Direct Mapping of Entity Category to Item Category ---
        # This ensures that each entity type drops its own unique loot.
        category_mapping = {
            'Insectoids': 'Insectoid',
            'Bandits': 'Bandit',
            'Aquatic': 'Aquatic',
            'Undead': 'Undead',
            'Beasts': 'Beast',
            'Goblins': 'Goblin',
            # These are not in your item list, so they will be skipped unless you add them.
            'Volcanic Beings': None, 
            'Automatons': None,
            'Swamp Dwellers': None,
        }

        # Ensure all required item categories exist.
        for item_cat_name in category_mapping.values():
            if item_cat_name:
                ItemCategory.objects.get_or_create(name=item_cat_name)
        self.stdout.write(self.style.SUCCESS('Verified all necessary ItemCategories exist.'))

        # Get all entities and iterate through them.
        entities = Entity.objects.all()
        if not entities:
            self.stdout.write(self.style.WARNING('No entities found in the database to seed.'))
            return

        seeded_count = 0
        for entity in entities:
            # Get the primary category of the entity.
            primary_category = entity.categories.first()
            if not primary_category:
                self.stdout.write(self.style.WARNING(f'Skipping entity "{entity.name}" as it has no primary category.'))
                continue

            # Find the corresponding item category from our mapping.
            item_category_name = category_mapping.get(primary_category.name)

            if item_category_name:
                try:
                    item_category = ItemCategory.objects.get(name=item_category_name)
                    # Using .set() is the correct, idempotent way to assign a ManyToMany relationship.
                    entity.loot_categories.set([item_category])
                    seeded_count += 1
                    self.stdout.write(f'  - Seeded loot for: "{entity.name}" -> [{item_category.name}]')
                except ItemCategory.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Could not find ItemCategory "{item_category_name}" for entity "{entity.name}".'))
            else:
                self.stdout.write(self.style.WARNING(f'No item category mapping found for "{primary_category.name}". Skipping "{entity.name}".'))

        self.stdout.write(self.style.SUCCESS(f'--- Seeding Complete: {seeded_count} entities updated. ---'))
