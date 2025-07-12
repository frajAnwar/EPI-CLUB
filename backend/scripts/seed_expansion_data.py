
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

def seed_expansion_data():
    """
    Seeds the database with new thematic content: Goblins, Swamp, Robotic, and Volcanic.
    This script is idempotent and can be run multiple times without creating duplicates.
    """
    print("--- Starting Thematic Content Expansion Seeding ---")

    # 1. ========== CREATE NEW CATEGORIES ==========
    print("\nStep 1: Creating new Item and Entity Categories...")
    cat_goblin_scrap, _ = ItemCategory.objects.get_or_create(name='Goblin Scrap')
    cat_swamp_reagents, _ = ItemCategory.objects.get_or_create(name='Swamp Reagents')
    cat_mech_parts, _ = ItemCategory.objects.get_or_create(name='Mechanical Parts')
    cat_igneous_essences, _ = ItemCategory.objects.get_or_create(name='Igneous Essences')

    ent_cat_goblins, _ = EntityCategory.objects.get_or_create(name='Goblins')
    ent_cat_swamp, _ = EntityCategory.objects.get_or_create(name='Swamp Dwellers')
    ent_cat_automatons, _ = EntityCategory.objects.get_or_create(name='Automatons')
    ent_cat_volcanic, _ = EntityCategory.objects.get_or_create(name='Volcanic Beings')

    # 2. ========== GOBLIN CONTENT (D-RANK) ==========
    print("\nStep 2: Seeding D-Rank Goblin Content...")
    veridian_forest, _ = WorldZone.objects.get_or_create(name='Veridian Forest', defaults={'rank_pool': ['E', 'D']})
    
    # Dungeon
    goblin_warren, _ = Dungeon.objects.get_or_create(
        name="Goblin Warren",
        defaults={'rank': 'D', 'zone': veridian_forest, 'description': 'A filthy, sprawling warren of goblin-kind.'}
    )
    goblin_warren.entity_categories.add(ent_cat_goblins)
    goblin_warren.item_categories.add(cat_goblin_scrap)

    # Entities & Items
    goblin_berserker, _ = Entity.objects.get_or_create(name='Goblin Berserker', defaults={'rank': 'D', 'power': 45, 'entity_type': 'minion'})
    goblin_berserker.categories.add(ent_cat_goblins)
    
    hobgoblin, _ = Entity.objects.get_or_create(name='Hobgoblin Chieftain', defaults={'rank': 'D', 'power': 140, 'entity_type': 'final_boss'})
    hobgoblin.categories.add(ent_cat_goblins)

    shiv, _ = Item.objects.get_or_create(name='Crude Goblin Shiv', defaults={'rarity': 'common', 'power': 3})
    shiv.categories.add(cat_goblin_scrap)

    goblin_archer, _ = Entity.objects.get_or_create(name='Goblin Archer', defaults={'rank': 'D', 'power': 40, 'entity_type': 'minion'})
    goblin_archer.categories.add(ent_cat_goblins)

    shiny_rocks, _ = Item.objects.get_or_create(name='Sack of Shiny Rocks', defaults={'rarity': 'common', 'power': 0})
    shiny_rocks.categories.add(cat_goblin_scrap)

    # 3. ========== SWAMP CONTENT (C-RANK) ==========
    print("\nStep 3: Seeding C-Rank Swamp Content...")
    swamp_zone, _ = WorldZone.objects.get_or_create(name='Fetid Swamp', defaults={'rank_pool': ['C']})

    # Dungeon
    troll_lair, _ = Dungeon.objects.get_or_create(
        name="Bog-Troll's Lair",
        defaults={'rank': 'C', 'zone': swamp_zone, 'description': 'A damp cave reeking of mud and decay.'}
    )
    troll_lair.entity_categories.add(ent_cat_swamp)
    troll_lair.item_categories.add(cat_swamp_reagents)

    # Entities & Items
    leech, _ = Entity.objects.get_or_create(name='Giant Leech', defaults={'rank': 'C', 'power': 70, 'entity_type': 'minion'})
    leech.categories.add(ent_cat_swamp)

    bog_troll, _ = Entity.objects.get_or_create(name='Bog-Troll', defaults={'rank': 'C', 'power': 220, 'entity_type': 'final_boss'})
    bog_troll.categories.add(ent_cat_swamp)

    troll_blood, _ = Item.objects.get_or_create(name='Congealed Troll Blood', defaults={'rarity': 'rare', 'power': 0})
    troll_blood.categories.add(cat_swamp_reagents)

    mire_fly, _ = Entity.objects.get_or_create(name='Venomous Mire-Fly', defaults={'rank': 'C', 'power': 65, 'entity_type': 'minion'})
    mire_fly.categories.add(ent_cat_swamp)

    fen_witch, _ = Entity.objects.get_or_create(name='Witch of the Fen', defaults={'rank': 'C', 'power': 150, 'entity_type': 'boss'})
    fen_witch.categories.add(ent_cat_swamp)

    fen_lily, _ = Item.objects.get_or_create(name='Glimmering Fen-Lily', defaults={'rarity': 'uncommon', 'power': 0})
    fen_lily.categories.add(cat_swamp_reagents)

    # 4. ========== ROBOTIC CONTENT (B-RANK) ==========
    print("\nStep 4: Seeding B-Rank Robotic Content...")
    scrap_zone, _ = WorldZone.objects.get_or_create(name='The Scrapheap', defaults={'rank_pool': ['B']})

    # Dungeon
    factory, _ = Dungeon.objects.get_or_create(
        name="Assembly Line Omega",
        defaults={'rank': 'B', 'zone': scrap_zone, 'description': 'A defunct automated factory that still hums with dangerous energy.'}
    )
    factory.entity_categories.add(ent_cat_automatons)
    factory.item_categories.add(cat_mech_parts)

    # Entities & Items
    sentry_drone, _ = Entity.objects.get_or_create(name='Sentry Drone', defaults={'rank': 'B', 'power': 180, 'entity_type': 'minion'})
    sentry_drone.categories.add(ent_cat_automatons)

    guardian, _ = Entity.objects.get_or_create(name='Assembly Guardian', defaults={'rank': 'B', 'power': 450, 'entity_type': 'final_boss'})
    guardian.categories.add(ent_cat_automatons)

    servo, _ = Item.objects.get_or_create(name='High-Torque Servo Motor', defaults={'rarity': 'epic', 'power': 0})
    servo.categories.add(cat_mech_parts)

    repair_bot, _ = Entity.objects.get_or_create(name='Malfunctioning Repair Bot', defaults={'rank': 'B', 'power': 170, 'entity_type': 'minion'})
    repair_bot.categories.add(ent_cat_automatons)

    hk_prototype, _ = Entity.objects.get_or_create(name='Hunter-Killer Prototype', defaults={'rank': 'B', 'power': 300, 'entity_type': 'boss'})
    hk_prototype.categories.add(ent_cat_automatons)

    sensor_array, _ = Item.objects.get_or_create(name='Pristine Sensor Array', defaults={'rarity': 'rare', 'power': 0})
    sensor_array.categories.add(cat_mech_parts)

    # 5. ========== VOLCANIC CONTENT (A-RANK) ==========
    print("\nStep 5: Seeding A-Rank Volcanic Content...")
    volcano_zone, _ = WorldZone.objects.get_or_create(name='Cinderpeak', defaults={'rank_pool': ['A']})

    # Dungeon
    magma_core, _ = Dungeon.objects.get_or_create(
        name="The Magma Core",
        defaults={'rank': 'A', 'zone': volcano_zone, 'description': 'A cavern leading to the fiery heart of the volcano.'}
    )
    magma_core.entity_categories.add(ent_cat_volcanic)
    magma_core.item_categories.add(cat_igneous_essences)

    # Entities & Items
    lava_elemental, _ = Entity.objects.get_or_create(name='Lava Elemental', defaults={'rank': 'A', 'power': 350, 'entity_type': 'minion'})
    lava_elemental.categories.add(ent_cat_volcanic)

    obsidian_golem, _ = Entity.objects.get_or_create(name='Obsidian Golem', defaults={'rank': 'A', 'power': 800, 'entity_type': 'final_boss'})
    obsidian_golem.categories.add(ent_cat_volcanic)

    heart_of_magma, _ = Item.objects.get_or_create(name='Heart of Magma', defaults={'rarity': 'legendary', 'power': 0})
    heart_of_magma.categories.add(cat_igneous_essences)

    cinder_imp, _ = Entity.objects.get_or_create(name='Cinder Imp', defaults={'rank': 'A', 'power': 330, 'entity_type': 'minion'})
    cinder_imp.categories.add(ent_cat_volcanic)

    magma_hydra, _ = Entity.objects.get_or_create(name='Magma Hydra', defaults={'rank': 'A', 'power': 600, 'entity_type': 'boss'})
    magma_hydra.categories.add(ent_cat_volcanic)

    obsidian_shard, _ = Item.objects.get_or_create(name='Razor-Sharp Obsidian Shard', defaults={'rarity': 'uncommon', 'power': 0})
    obsidian_shard.categories.add(cat_igneous_essences)

    print("\n--- Thematic Content Expansion Seeding Completed ---")

if __name__ == '__main__':
    seed_expansion_data()
