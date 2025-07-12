
import os
import django
import sys

# Add the backend directory to the Python path for standalone script execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_rpg.settings')
django.setup()

from items.models import Item, ItemCategory
from dungeons.models import Entity, EntityCategory

def seed_expansion_entities():
    """
    Seeds the database with additional E and D-Rank entities and their related items.
    This script assumes that the base categories and dungeons already exist.
    """
    print("--- Starting Entity Expansion Seeding ---")

    # 1. ========== GET EXISTING CATEGORIES ==========
    print("\nStep 1: Fetching existing categories...")
    try:
        # Item Categories
        cat_weapon, _ = ItemCategory.objects.get_or_create(name='Weapon')
        cat_armor, _ = ItemCategory.objects.get_or_create(name='Armor')
        cat_crafting, _ = ItemCategory.objects.get_or_create(name='Crafting Material')
        theme_goblin, _ = ItemCategory.objects.get_or_create(name='Goblin')
        theme_beast, _ = ItemCategory.objects.get_or_create(name='Beast')
        theme_undead, _ = ItemCategory.objects.get_or_create(name='Undead')
        theme_aquatic, _ = ItemCategory.objects.get_or_create(name='Aquatic')

        # Entity Categories
        ent_cat_goblins = EntityCategory.objects.get(name='Goblins')
        ent_cat_beasts = EntityCategory.objects.get(name='Beasts')
        ent_cat_undead = EntityCategory.objects.get(name='Undead')
        ent_cat_aquatic = EntityCategory.objects.get(name='Aquatic')
    except (ItemCategory.DoesNotExist, EntityCategory.DoesNotExist) as e:
        print(f"Error: A required category does not exist. Please run the main seeding script first. Details: {e}")
        return

    # 2. ========== ADD NEW E-RANK ENTITIES AND ITEMS ==========
    print("\nStep 2: Seeding new E-Rank entities and items...")

    # Goblin Expansion
    Entity.objects.get_or_create(name='Goblin Archer', defaults={'rank': 'E', 'power': 10, 'entity_type': 'minion'}).categories.add(ent_cat_goblins)
    Entity.objects.get_or_create(name='Goblin Taskmaster', defaults={'rank': 'E', 'power': 35, 'entity_type': 'boss'}).categories.add(ent_cat_goblins)
    Item.objects.get_or_create(name='Flimsy Goblin Bow', defaults={'rarity': 'common'}).categories.add(cat_weapon, theme_goblin)

    # Beast Expansion
    Entity.objects.get_or_create(name='Giant Forest Spider', defaults={'rank': 'E', 'power': 15, 'entity_type': 'minion'}).categories.add(ent_cat_beasts)
    Entity.objects.get_or_create(name='Enraged Bear', defaults={'rank': 'E', 'power': 40, 'entity_type': 'boss'}).categories.add(ent_cat_beasts)
    Item.objects.get_or_create(name='Thick Bear Pelt', defaults={'rarity': 'uncommon'}).categories.add(cat_crafting, theme_beast)

    # Aquatic Expansion
    Entity.objects.get_or_create(name='Swamp Lurker', defaults={'rank': 'E', 'power': 12, 'entity_type': 'minion'}).categories.add(ent_cat_aquatic)
    Entity.objects.get_or_create(name='Giant Snapping Turtle', defaults={'rank': 'E', 'power': 38, 'entity_type': 'boss'}).categories.add(ent_cat_aquatic)
    Item.objects.get_or_create(name='Hard Turtle Scute', defaults={'rarity': 'uncommon'}).categories.add(cat_armor, theme_aquatic) # Can be used as a shield/armor piece

    # Undead Expansion
    Entity.objects.get_or_create(name='Shambling Zombie', defaults={'rank': 'E', 'power': 9, 'entity_type': 'minion'}).categories.add(ent_cat_undead)
    Entity.objects.get_or_create(name='Skeletal Captain', defaults={'rank': 'E', 'power': 36, 'entity_type': 'boss'}).categories.add(ent_cat_undead)
    Item.objects.get_or_create(name='Tattered Captain\'s Sash', defaults={'rarity': 'uncommon'}).categories.add(cat_crafting, theme_undead)

    === ADD NEW D-RANK ENTITIES AND ITEMS
