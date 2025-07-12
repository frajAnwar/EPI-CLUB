
import os
import django
import sys

# Add the backend directory to the Python path for standalone script execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_rpg.settings')
django.setup()

from items.models import Item, ItemCategory
from dungeons.models import Dungeon, Entity, EntityCategory, WorldZone

def seed_world():
    """
    Seeds the entire game world from scratch with a unified vision:
    - 1 World Zone for E and D ranks.
    - 4 E-Rank dungeons with a full ecosystem of entities and items.
    - 4 D-Rank dungeons with a full ecosystem of entities and items.
    This script is idempotent and can be run multiple times without creating duplicates.
    """
    print("--- Starting Full World Seeding ---")

    # 1. ========== FOUNDATIONAL & THEMATIC ITEM CATEGORIES ==========
    print("\nStep 1: Creating Item Categories...")
    cat_weapon, _ = ItemCategory.objects.get_or_create(name='Weapon')
    cat_armor, _ = ItemCategory.objects.get_or_create(name='Armor')
    cat_trinket, _ = ItemCategory.objects.get_or_create(name='Trinket')
    cat_crafting, _ = ItemCategory.objects.get_or_create(name='Crafting Material')
    cat_consumable, _ = ItemCategory.objects.get_or_create(name='Consumable')

    theme_goblin, _ = ItemCategory.objects.get_or_create(name='Goblin')
    theme_beast, _ = ItemCategory.objects.get_or_create(name='Beast')
    theme_undead, _ = ItemCategory.objects.get_or_create(name='Undead')
    theme_aquatic, _ = ItemCategory.objects.get_or_create(name='Aquatic')
    theme_bandit, _ = ItemCategory.objects.get_or_create(name='Bandit')
    theme_insectoid, _ = ItemCategory.objects.get_or_create(name='Insectoid')

    # 2. ========== ENTITY CATEGORIES ==========
    print("\nStep 2: Creating Entity Categories...")
    ent_cat_goblins, _ = EntityCategory.objects.get_or_create(name='Goblins')
    ent_cat_beasts, _ = EntityCategory.objects.get_or_create(name='Beasts')
    ent_cat_undead, _ = EntityCategory.objects.get_or_create(name='Undead')
    ent_cat_aquatic, _ = EntityCategory.objects.get_or_create(name='Aquatic')
    ent_cat_bandits, _ = EntityCategory.objects.get_or_create(name='Bandits')
    ent_cat_insectoids, _ = EntityCategory.objects.get_or_create(name='Insectoids')

    # 3. ========== WORLD ZONE ==========
    print("\nStep 3: Creating the World Zone...")
    main_zone, _ = WorldZone.objects.get_or_create(
        name='The Sundered Marches',
        defaults={'rank_pool': ['E', 'D'], 'description': 'A vast and varied landscape where new hunters test their mettle.'}
    )
    main_zone.rank_pool = ['E', 'D']
    main_zone.save()

    # 4. ========== E-RANK DUNGEONS & ECOSYSTEMS ==========
    print("\nStep 4: Seeding E-Rank Dungeons...")

    # --- E-Dungeon 1: Goblin Cave ---
    d_goblin, _ = Dungeon.objects.get_or_create(name='Goblin Cave', defaults={'rank': 'E', 'zone': main_zone})
    d_goblin.entity_categories.add(ent_cat_goblins)
    d_goblin.item_categories.add(theme_goblin)
    # Minions
    e, _ = Entity.objects.get_or_create(name='Goblin Cutthroat', defaults={'rank': 'E', 'power': 12, 'entity_type': 'minion'}); e.categories.add(ent_cat_goblins)
    e, _ = Entity.objects.get_or_create(name='Goblin Slinger', defaults={'rank': 'E', 'power': 10, 'entity_type': 'minion'}); e.categories.add(ent_cat_goblins)
    e, _ = Entity.objects.get_or_create(name='Goblin Sneak', defaults={'rank': 'E', 'power': 8, 'entity_type': 'minion'}); e.categories.add(ent_cat_goblins)
    e, _ = Entity.objects.get_or_create(name='Goblin Rock-thrower', defaults={'rank': 'E', 'power': 9, 'entity_type': 'minion'}); e.categories.add(ent_cat_goblins)
    e, _ = Entity.objects.get_or_create(name='Goblin Wolfrider', defaults={'rank': 'E', 'power': 16, 'entity_type': 'minion'}); e.categories.add(ent_cat_goblins)
    e, _ = Entity.objects.get_or_create(name='Goblin Scavenger', defaults={'rank': 'E', 'power': 7, 'entity_type': 'minion'}); e.categories.add(ent_cat_goblins)
    # Bosses
    e, _ = Entity.objects.get_or_create(name='Goblin Taskmaster', defaults={'rank': 'E', 'power': 35, 'entity_type': 'boss'}); e.categories.add(ent_cat_goblins)
    e, _ = Entity.objects.get_or_create(name='Goblin Shaman', defaults={'rank': 'E', 'power': 38, 'entity_type': 'boss'}); e.categories.add(ent_cat_goblins)
    e, _ = Entity.objects.get_or_create(name='Goblin Alchemist', defaults={'rank': 'E', 'power': 33, 'entity_type': 'boss'}); e.categories.add(ent_cat_goblins)
    e, _ = Entity.objects.get_or_create(name='Goblin War-Chief', defaults={'rank': 'E', 'power': 40, 'entity_type': 'boss'}); e.categories.add(ent_cat_goblins)
    # Final Bosses
    e, _ = Entity.objects.get_or_create(name='Chief Grub-Snout', defaults={'rank': 'E', 'power': 55, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_goblins)
    e, _ = Entity.objects.get_or_create(name='Hobgoblin Commander', defaults={'rank': 'E', 'power': 58, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_goblins)
    # Items
    i, _ = Item.objects.get_or_create(name='Shamanic Totem', defaults={'rarity': 'uncommon'}); i.categories.add(cat_trinket, theme_goblin)
    i, _ = Item.objects.get_or_create(name='Crude Shiv', defaults={'rarity': 'common'}); i.categories.add(cat_weapon, theme_goblin)
    i, _ = Item.objects.get_or_create(name='Scrap-Metal Pauldron', defaults={'rarity': 'common'}); i.categories.add(cat_armor, theme_goblin)
    i, _ = Item.objects.get_or_create(name='Volatile Concoction', defaults={'rarity': 'uncommon'}); i.categories.add(cat_consumable, theme_goblin)

    # --- E-Dungeon 2: Whispering Den ---
    d_wolf, _ = Dungeon.objects.get_or_create(name='Whispering Den', defaults={'rank': 'E', 'zone': main_zone})
    d_wolf.entity_categories.add(ent_cat_beasts)
    d_wolf.item_categories.add(theme_beast)
    # Minions
    e, _ = Entity.objects.get_or_create(name='Forest Wolf', defaults={'rank': 'E', 'power': 14, 'entity_type': 'minion'}); e.categories.add(ent_cat_beasts)
    e, _ = Entity.objects.get_or_create(name='Giant Forest Spider', defaults={'rank': 'E', 'power': 15, 'entity_type': 'minion'}); e.categories.add(ent_cat_beasts)
    e, _ = Entity.objects.get_or_create(name='Dire Bat', defaults={'rank': 'E', 'power': 11, 'entity_type': 'minion'}); e.categories.add(ent_cat_beasts)
    e, _ = Entity.objects.get_or_create(name='Giant Scorpion', defaults={'rank': 'E', 'power': 13, 'entity_type': 'minion'}); e.categories.add(ent_cat_beasts)
    e, _ = Entity.objects.get_or_create(name='Shadow Cat', defaults={'rank': 'E', 'power': 16, 'entity_type': 'minion'}); e.categories.add(ent_cat_beasts)
    e, _ = Entity.objects.get_or_create(name='Grizzly Bear Cub', defaults={'rank': 'E', 'power': 12, 'entity_type': 'minion'}); e.categories.add(ent_cat_beasts)
    # Bosses
    e, _ = Entity.objects.get_or_create(name='Enraged Bear', defaults={'rank': 'E', 'power': 40, 'entity_type': 'boss'}); e.categories.add(ent_cat_beasts)
    e, _ = Entity.objects.get_or_create(name='Ancient Boar', defaults={'rank': 'E', 'power': 42, 'entity_type': 'boss'}); e.categories.add(ent_cat_beasts)
    e, _ = Entity.objects.get_or_create(name='Alpha Wolf', defaults={'rank': 'E', 'power': 38, 'entity_type': 'boss'}); e.categories.add(ent_cat_beasts)
    e, _ = Entity.objects.get_or_create(name='Roc Matriarch', defaults={'rank': 'E', 'power': 44, 'entity_type': 'boss'}); e.categories.add(ent_cat_beasts)
    # Final Bosses
    e, _ = Entity.objects.get_or_create(name='The Great White Wolf', defaults={'rank': 'E', 'power': 60, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_beasts)
    e, _ = Entity.objects.get_or_create(name='Mother of Spiders', defaults={'rank': 'E', 'power': 62, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_beasts)
    # Items
    i, _ = Item.objects.get_or_create(name='Spider Silk', defaults={'rarity': 'common'}); i.categories.add(cat_crafting, theme_beast)
    i, _ = Item.objects.get_or_create(name='Wolf Pelt', defaults={'rarity': 'common'}); i.categories.add(cat_crafting, theme_beast)
    i, _ = Item.objects.get_or_create(name='Wolf-Fang Charm', defaults={'rarity': 'uncommon'}); i.categories.add(cat_trinket, theme_beast)
    i, _ = Item.objects.get_or_create(name='Giant Roc Feather', defaults={'rarity': 'rare'}); i.categories.add(cat_crafting, theme_beast)

    # --- E-Dungeon 3: Flooded Crypt ---
    d_flooded, _ = Dungeon.objects.get_or_create(name='Flooded Crypt', defaults={'rank': 'E', 'zone': main_zone})
    d_flooded.entity_categories.add(ent_cat_aquatic)
    d_flooded.item_categories.add(theme_aquatic)
    # Minions
    e, _ = Entity.objects.get_or_create(name='Giant Coral Crab', defaults={'rank': 'E', 'power': 13, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Swamp Lurker', defaults={'rank': 'E', 'power': 12, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Giant Leech', defaults={'rank': 'E', 'power': 10, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Piranha Swarm', defaults={'rank': 'E', 'power': 18, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='River Serpent', defaults={'rank': 'E', 'power': 15, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Mirefolk Hunter', defaults={'rank': 'E', 'power': 14, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    # Bosses
    e, _ = Entity.objects.get_or_create(name='Giant Snapping Turtle', defaults={'rank': 'E', 'power': 38, 'entity_type': 'boss'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Murkwater Serpent', defaults={'rank': 'E', 'power': 41, 'entity_type': 'boss'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Swamp Hag', defaults={'rank': 'E', 'power': 37, 'entity_type': 'boss'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Giant Crab', defaults={'rank': 'E', 'power': 43, 'entity_type': 'boss'}); e.categories.add(ent_cat_aquatic)
    # Final Bosses
    e, _ = Entity.objects.get_or_create(name='Tide-Caller Fishman', defaults={'rank': 'E', 'power': 58, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Crypt Hydra', defaults={'rank': 'E', 'power': 61, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_aquatic)
    # Items
    i, _ = Item.objects.get_or_create(name='Serpent Scale', defaults={'rarity': 'uncommon'}); i.categories.add(cat_crafting, theme_aquatic)
    i, _ = Item.objects.get_or_create(name='Coral-Encrusted Helm', defaults={'rarity': 'uncommon'}); i.categories.add(cat_armor, theme_aquatic)
    i, _ = Item.objects.get_or_create(name="Fishman's Spear", defaults={'rarity': 'uncommon'}); i.categories.add(cat_weapon, theme_aquatic)
    i, _ = Item.objects.get_or_create(name="Hag's Hex-doll", defaults={'rarity': 'rare'}); i.categories.add(cat_trinket, theme_aquatic)

    # --- E-Dungeon 4: Restless Graveyard ---
    d_graveyard, _ = Dungeon.objects.get_or_create(name='Restless Graveyard', defaults={'rank': 'E', 'zone': main_zone})
    d_graveyard.entity_categories.add(ent_cat_undead)
    d_graveyard.item_categories.add(theme_undead)
    # Minions
    e, _ = Entity.objects.get_or_create(name='Risen Skeleton', defaults={'rank': 'E', 'power': 11, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Shambling Zombie', defaults={'rank': 'E', 'power': 9, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Ghoul', defaults={'rank': 'E', 'power': 12, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Screaming Skull', defaults={'rank': 'E', 'power': 14, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Zombie Hulk', defaults={'rank': 'E', 'power': 17, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Corpse-Rat Swarm', defaults={'rank': 'E', 'power': 13, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    # Bosses
    e, _ = Entity.objects.get_or_create(name='Skeletal Captain', defaults={'rank': 'E', 'power': 36, 'entity_type': 'boss'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Crypt Wraith', defaults={'rank': 'E', 'power': 39, 'entity_type': 'boss'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name="Necromancer's Apprentice", defaults={'rank': 'E', 'power': 35, 'entity_type': 'boss'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Grave Warden', defaults={'rank': 'E', 'power': 41, 'entity_type': 'boss'}); e.categories.add(ent_cat_undead)
    # Final Bosses
    e, _ = Entity.objects.get_or_create(name='Cemetery Ghoul', defaults={'rank': 'E', 'power': 56, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Banshee', defaults={'rank': 'E', 'power': 59, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_undead)
    # Items
    i, _ = Item.objects.get_or_create(name="Banshee's Veil", defaults={'rarity': 'rare'}); i.categories.add(cat_armor, theme_undead)
    i, _ = Item.objects.get_or_create(name='Grave Dust', defaults={'rarity': 'common'}); i.categories.add(cat_crafting, theme_undead)
    i, _ = Item.objects.get_or_create(name='Potion of Minor Undeath', defaults={'rarity': 'uncommon'}); i.categories.add(cat_consumable, theme_undead)
    i, _ = Item.objects.get_or_create(name="Warden's Key", defaults={'rarity': 'rare'}); i.categories.add(cat_trinket, theme_undead)

    # 5. ========== D-RANK DUNGEONS & ECOSYSTEMS ==========
    print("\nStep 5: Seeding D-Rank Dungeons...")

    # --- D-Dungeon 1: Bandit Hideout ---
    d_bandit, _ = Dungeon.objects.get_or_create(name='Bandit Hideout', defaults={'rank': 'D', 'zone': main_zone})
    d_bandit.entity_categories.add(ent_cat_bandits)
    d_bandit.item_categories.add(theme_bandit)
    # Minions
    e, _ = Entity.objects.get_or_create(name='Highwayman Archer', defaults={'rank': 'D', 'power': 40, 'entity_type': 'minion'}); e.categories.add(ent_cat_bandits)
    e, _ = Entity.objects.get_or_create(name='Bandit Thug', defaults={'rank': 'D', 'power': 38, 'entity_type': 'minion'}); e.categories.add(ent_cat_bandits)
    e, _ = Entity.objects.get_or_create(name='Bandit Cutpurse', defaults={'rank': 'D', 'power': 36, 'entity_type': 'minion'}); e.categories.add(ent_cat_bandits)
    e, _ = Entity.objects.get_or_create(name='Corrupt Sellsword', defaults={'rank': 'D', 'power': 41, 'entity_type': 'minion'}); e.categories.add(ent_cat_bandits)
    e, _ = Entity.objects.get_or_create(name='Bandit Enforcer', defaults={'rank': 'D', 'power': 44, 'entity_type': 'minion'}); e.categories.add(ent_cat_bandits)
    e, _ = Entity.objects.get_or_create(name='War Dog', defaults={'rank': 'D', 'power': 39, 'entity_type': 'minion'}); e.categories.add(ent_cat_bandits)
    # Bosses
    e, _ = Entity.objects.get_or_create(name='Bandit Lieutenant', defaults={'rank': 'D', 'power': 90, 'entity_type': 'boss'}); e.categories.add(ent_cat_bandits)
    e, _ = Entity.objects.get_or_create(name='Hedge Mage', defaults={'rank': 'D', 'power': 95, 'entity_type': 'boss'}); e.categories.add(ent_cat_bandits)
    e, _ = Entity.objects.get_or_create(name='Bandit Quartermaster', defaults={'rank': 'D', 'power': 92, 'entity_type': 'boss'}); e.categories.add(ent_cat_bandits)
    e, _ = Entity.objects.get_or_create(name='Bandit Assassin', defaults={'rank': 'D', 'power': 100, 'entity_type': 'boss'}); e.categories.add(ent_cat_bandits)
    # Final Bosses
    e, _ = Entity.objects.get_or_create(name='Captain "One-Eye" Joric', defaults={'rank': 'D', 'power': 140, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_bandits)
    e, _ = Entity.objects.get_or_create(name='The Shadow of the Marches', defaults={'rank': 'D', 'power': 145, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_bandits)
    # Items
    i, _ = Item.objects.get_or_create(name="Assassin's Dagger", defaults={'rarity': 'rare'}); i.categories.add(cat_weapon, theme_bandit)
    i, _ = Item.objects.get_or_create(name='Stolen Steel Longsword', defaults={'rarity': 'uncommon'}); i.categories.add(cat_weapon, theme_bandit)
    i, _ = Item.objects.get_or_create(name="Highwayman's Leather Jerkin", defaults={'rarity': 'uncommon'}); i.categories.add(cat_armor, theme_bandit)
    i, _ = Item.objects.get_or_create(name='Poisoned Throwing Knives', defaults={'rarity': 'rare'}); i.categories.add(cat_consumable, theme_bandit)

    # --- D-Dungeon 2: Chittering Hive ---
    d_hive, _ = Dungeon.objects.get_or_create(name='Chittering Hive', defaults={'rank': 'D', 'zone': main_zone})
    d_hive.entity_categories.add(ent_cat_insectoids)
    d_hive.item_categories.add(theme_insectoid)
    # Minions
    e, _ = Entity.objects.get_or_create(name='Giant Hive Soldier', defaults={'rank': 'D', 'power': 45, 'entity_type': 'minion'}); e.categories.add(ent_cat_insectoids)
    e, _ = Entity.objects.get_or_create(name='Venomous Spitter', defaults={'rank': 'D', 'power': 42, 'entity_type': 'minion'}); e.categories.add(ent_cat_insectoids)
    e, _ = Entity.objects.get_or_create(name='Giant Wasp', defaults={'rank': 'D', 'power': 39, 'entity_type': 'minion'}); e.categories.add(ent_cat_insectoids)
    e, _ = Entity.objects.get_or_create(name='Acid-spitting Beetle', defaults={'rank': 'D', 'power': 43, 'entity_type': 'minion'}); e.categories.add(ent_cat_insectoids)
    e, _ = Entity.objects.get_or_create(name='Burrowing Larva', defaults={'rank': 'D', 'power': 35, 'entity_type': 'minion'}); e.categories.add(ent_cat_insectoids)
    e, _ = Entity.objects.get_or_create(name='Scuttling Swarmling', defaults={'rank': 'D', 'power': 33, 'entity_type': 'minion'}); e.categories.add(ent_cat_insectoids)
    # Bosses
    e, _ = Entity.objects.get_or_create(name='Hive Guardian', defaults={'rank': 'D', 'power': 100, 'entity_type': 'boss'}); e.categories.add(ent_cat_insectoids)
    e, _ = Entity.objects.get_or_create(name='Giant Mantis', defaults={'rank': 'D', 'power': 105, 'entity_type': 'boss'}); e.categories.add(ent_cat_insectoids)
    e, _ = Entity.objects.get_or_create(name='Centipede Horror', defaults={'rank': 'D', 'power': 98, 'entity_type': 'boss'}); e.categories.add(ent_cat_insectoids)
    e, _ = Entity.objects.get_or_create(name='Mantis Lord', defaults={'rank': 'D', 'power': 110, 'entity_type': 'boss'}); e.categories.add(ent_cat_insectoids)
    # Final Bosses
    e, _ = Entity.objects.get_or_create(name='The Hive Queen', defaults={'rank': 'D', 'power': 150, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_insectoids)
    e, _ = Entity.objects.get_or_create(name='The Broodmother', defaults={'rank': 'D', 'power': 155, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_insectoids)
    # Items
    i, _ = Item.objects.get_or_create(name="Broodmother's Egg", defaults={'rarity': 'epic'}); i.categories.add(cat_trinket, theme_insectoid)
    i, _ = Item.objects.get_or_create(name='Chitin Plate', defaults={'rarity': 'uncommon'}); i.categories.add(cat_crafting, theme_insectoid)
    i, _ = Item.objects.get_or_create(name="Queen's Stinger", defaults={'rarity': 'rare'}); i.categories.add(cat_weapon, theme_insectoid)
    i, _ = Item.objects.get_or_create(name='Corrosive Acid Gland', defaults={'rarity': 'rare'}); i.categories.add(cat_crafting, theme_insectoid)

    # --- D-Dungeon 3: Sunken Temple ---
    d_temple, _ = Dungeon.objects.get_or_create(name='Sunken Temple', defaults={'rank': 'D', 'zone': main_zone})
    d_temple.entity_categories.add(ent_cat_aquatic)
    d_temple.item_categories.add(theme_aquatic)
    # Minions
    e, _ = Entity.objects.get_or_create(name='Temple Naga', defaults={'rank': 'D', 'power': 42, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Deep Sea Angler', defaults={'rank': 'D', 'power': 44, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Kelp Horror', defaults={'rank': 'D', 'power': 40, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Shark-man Warrior', defaults={'rank': 'D', 'power': 48, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Giant Electric Eel', defaults={'rank': 'D', 'power': 46, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Coral Golem', defaults={'rank': 'D', 'power': 50, 'entity_type': 'minion'}); e.categories.add(ent_cat_aquatic)
    # Bosses
    e, _ = Entity.objects.get_or_create(name='Leviathan Hatchling', defaults={'rank': 'D', 'power': 110, 'entity_type': 'boss'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Temple Guardian Golem', defaults={'rank': 'D', 'power': 115, 'entity_type': 'boss'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Siren', defaults={'rank': 'D', 'power': 90, 'entity_type': 'boss'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='Kraken Spawn', defaults={'rank': 'D', 'power': 120, 'entity_type': 'boss'}); e.categories.add(ent_cat_aquatic)
    # Final Bosses
    e, _ = Entity.objects.get_or_create(name='Hydra of the Depths', defaults={'rank': 'D', 'power': 145, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_aquatic)
    e, _ = Entity.objects.get_or_create(name='The Sunken King', defaults={'rank': 'D', 'power': 152, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_aquatic)
    # Items
    i, _ = Item.objects.get_or_create(name='Crown of the Sunken King', defaults={'rarity': 'epic'}); i.categories.add(cat_armor, theme_aquatic)
    i, _ = Item.objects.get_or_create(name='Naga Scale Cloak', defaults={'rarity': 'rare'}); i.categories.add(cat_armor, theme_aquatic)
    i, _ = Item.objects.get_or_create(name='Ring of the Deeps', defaults={'rarity': 'rare'}); i.categories.add(cat_trinket, theme_aquatic)
    i, _ = Item.objects.get_or_create(name="Siren's Voicebox", defaults={'rarity': 'epic'}); i.categories.add(cat_trinket, theme_aquatic)

    # --- D-Dungeon 4: Executioner's Crypt ---
    d_crypt, _ = Dungeon.objects.get_or_create(name="Executioner's Crypt", defaults={'rank': 'D', 'zone': main_zone})
    d_crypt.entity_categories.add(ent_cat_undead)
    d_crypt.item_categories.add(theme_undead)
    # Minions
    e, _ = Entity.objects.get_or_create(name='Crypt Wraith', defaults={'rank': 'D', 'power': 38, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Tortured Soul', defaults={'rank': 'D', 'power': 35, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Dread Knight', defaults={'rank': 'D', 'power': 50, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Vampire Spawn', defaults={'rank': 'D', 'power': 45, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Bone Golem', defaults={'rank': 'D', 'power': 55, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Flesh-Eating Ghoul', defaults={'rank': 'D', 'power': 42, 'entity_type': 'minion'}); e.categories.add(ent_cat_undead)
    # Bosses
    e, _ = Entity.objects.get_or_create(name='Tortured Spirit', defaults={'rank': 'D', 'power': 95, 'entity_type': 'boss'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Death Knight Acolyte', defaults={'rank': 'D', 'power': 102, 'entity_type': 'boss'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Lich Adept', defaults={'rank': 'D', 'power': 110, 'entity_type': 'boss'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='Abomination', defaults={'rank': 'D', 'power': 125, 'entity_type': 'boss'}); e.categories.add(ent_cat_undead)
    # Final Bosses
    e, _ = Entity.objects.get_or_create(name='The Headless Executioner', defaults={'rank': 'D', 'power': 148, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_undead)
    e, _ = Entity.objects.get_or_create(name='The Crypt Lord', defaults={'rank': 'D', 'power': 158, 'entity_type': 'final_boss'}); e.categories.add(ent_cat_undead)
    # Items
    i, _ = Item.objects.get_or_create(name="Lich's Phylactery", defaults={'rarity': 'epic'}); i.categories.add(cat_trinket, theme_undead)
    i, _ = Item.objects.get_or_create(name='Wraith Essence', defaults={'rarity': 'uncommon'}); i.categories.add(cat_crafting, theme_undead)
    i, _ = Item.objects.get_or_create(name="The Executioner's Great-Axe", defaults={'rarity': 'rare'}); i.categories.add(cat_weapon, theme_undead)
    i, _ = Item.objects.get_or_create(name='Vial of Vampiric Blood', defaults={'rarity': 'rare'}); i.categories.add(cat_consumable, theme_undead)

    print("\n--- Full World Seeding Completed ---\n")

if __name__ == '__main__':
    seed_world()
