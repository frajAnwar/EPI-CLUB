
import random
from dungeons.models import WorldZone, Dungeon, Entity, EntityCategory
from items.models import Item, ItemCategory

def run():
    print("--- Seeding E-Rank World Data ---")

    # 1. Create Item Categories
    print("Creating item categories...")
    weapon_cat, _ = ItemCategory.objects.get_or_create(name='Weapon')
    armor_cat, _ = ItemCategory.objects.get_or_create(name='Armor')
    material_cat, _ = ItemCategory.objects.get_or_create(name='Crafting Material')

    # 2. Create Items
    print("Creating items...")
    rusty_sword, _ = Item.objects.get_or_create(
        name='Rusty Shortsword',
        defaults={'rarity': 'common', 'base_price': 10, 'power': 5}
    )
    rusty_sword.categories.add(weapon_cat)

    worn_tunic, _ = Item.objects.get_or_create(
        name='Worn Leather Tunic',
        defaults={'rarity': 'common', 'base_price': 5, 'power': 3}
    )
    worn_tunic.categories.add(armor_cat)

    goblin_ear, _ = Item.objects.get_or_create(
        name='Goblin Ear',
        defaults={'rarity': 'common', 'base_price': 1}
    )
    goblin_ear.categories.add(material_cat)

    wolf_pelt, _ = Item.objects.get_or_create(
        name='Wolf Pelt',
        defaults={'rarity': 'common', 'base_price': 2}
    )
    wolf_pelt.categories.add(material_cat)

    # 3. Create Entity Categories
    print("Creating entity categories...")
    goblinoid_cat, _ = EntityCategory.objects.get_or_create(name='Goblinoid')
    beast_cat, _ = EntityCategory.objects.get_or_create(name='Beast')

    # 4. Create Entities
    print("Creating entities...")
    goblin_scout, _ = Entity.objects.get_or_create(
        name='Goblin Scout',
        defaults={
            'rank': 'E', 'entity_type': 'minion', 'power': 10,
            'min_xp': 5, 'max_xp': 10, 'min_coins': 1, 'max_coins': 5
        }
    )
    goblin_scout.categories.add(goblinoid_cat)
    goblin_scout.loot_categories.add(weapon_cat, material_cat)

    dire_wolf, _ = Entity.objects.get_or_create(
        name='Dire Wolf',
        defaults={
            'rank': 'E', 'entity_type': 'minion', 'power': 15,
            'min_xp': 8, 'max_xp': 15, 'min_coins': 2, 'max_coins': 8
        }
    )
    dire_wolf.categories.add(beast_cat)
    dire_wolf.loot_categories.add(material_cat)

    goblin_chieftain, _ = Entity.objects.get_or_create(
        name='Goblin Chieftain',
        defaults={
            'rank': 'E', 'entity_type': 'boss', 'power': 50,
            'min_xp': 50, 'max_xp': 75, 'min_coins': 20, 'max_coins': 40
        }
    )
    goblin_chieftain.categories.add(goblinoid_cat)
    goblin_chieftain.loot_categories.add(weapon_cat, armor_cat)

    # 5. Create World Zone
    print("Creating world zone...")
    starting_zone, _ = WorldZone.objects.get_or_create(
        name='Veridian Forest',
        defaults={'world_map_x': 500, 'world_map_y': 800}
    )

    # 6. Create Dungeons
    print("Creating dungeons...")
    goblin_cave, _ = Dungeon.objects.get_or_create(
        name='Goblin Cave',
        defaults={
            'rank': 'E', 'min_level': 1, 'max_level': 5,
            'zone': starting_zone
        }
    )
    goblin_cave.entity_categories.add(goblinoid_cat)
    goblin_cave.item_categories.add(weapon_cat, material_cat)

    wolf_den, _ = Dungeon.objects.get_or_create(
        name='Whispering Wolf Den',
        defaults={
            'rank': 'E', 'min_level': 3, 'max_level': 8,
            'zone': starting_zone
        }
    )
    wolf_den.entity_categories.add(beast_cat)
    wolf_den.item_categories.add(material_cat)

    print("--- Seeding Complete! ---")

# This allows the script to be run standalone
if __name__ == '__main__':
    run()
