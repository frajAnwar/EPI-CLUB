# dungeons/management/commands/seed_dungeon_ecosystem.py
from django.core.management.base import BaseCommand
from dungeons.models import Dungeon, Entity, EntityCategory
from items.models import ItemCategory
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = 'Seeds the database with Solo Leveling-inspired entities and dungeons with proper category relationships'

    def handle(self, *args, **options):
        self.stdout.write('Creating the hunter world ecosystem...')
        
        # Create entity categories (environment types)
        entity_categories = self.create_entity_categories()
        
        # Create item categories (loot types)
        item_categories = self.create_item_categories()
        
        # Create entities for each rank
        self.create_entities('E', 1, 3, 10, entity_categories)
        self.create_entities('D', 4, 8, 12, entity_categories)
        self.create_entities('C', 9, 19, 15, entity_categories)
        self.create_entities('B', 20, 40, 18, entity_categories)
        self.create_entities('A', 41, 60, 20, entity_categories)
        self.create_entities('S', 61, 70, 15, entity_categories)
        self.create_entities('SS', 71, 90, 10, entity_categories)
        self.create_entities('SSS', 91, 100, 8, entity_categories)
        self.create_entities('National', 101, 120, 5, entity_categories)
        
        # Create dungeons
        self.create_dungeons(entity_categories, item_categories)
        
        self.stdout.write(self.style.SUCCESS('Successfully created the Solo Leveling-inspired dungeon ecosystem!'))
    
    def create_entity_categories(self):
        categories = {
            'Forest': 'Wild, untamed woodlands teeming with beasts',
            'Crypt': 'Tombs where spirits linger and undead rise',
            'Foundry': 'Industrial complexes with malfunctioning constructs',
            'Volcano': 'Fiery mountains home to fire creatures',
            'Ruins': 'Remnants of ancient civilizations',
            'Caverns': 'Deep cave systems with mineral guardians',
            'Swamp': 'Fetid marshlands filled with toxic life',
            'Sky Citadel': 'Floating islands accessible only by flight',
            'Ethereal': 'Realms blending physical and spiritual',
            'Dragonkin': 'Places touched by draconic essence',
            'Undead': 'Domains ruled by the restless dead',
            'Demon': 'Planes corrupted by demonic energy',
            'Ice': 'Frozen wastelands of eternal winter',
            'Desert': 'Scorching sands hiding ancient secrets',
            'Ocean': 'Underwater realms of aquatic beings',
        }
        
        created_categories = {}
        for name, desc in categories.items():
            cat, _ = EntityCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            created_categories[name] = cat
        return created_categories
    
    def create_item_categories(self):
        categories = {
            'Weapon': 'Tools of combat and destruction',
            'Armor': 'Protective gear for hunters',
            'Accessory': 'Magical trinkets and jewelry',
            'Consumable': 'Potions and temporary boosts',
            'Material': 'Crafting components from monsters',
            'Skill Book': 'Manuals that teach special abilities',
            'Artifact': 'Ancient relics with powerful magic',
            'Core': 'Monster essence crystals',
            'Dungeon Key': 'Keys that unlock special gates',
            'Hunter License': 'Identification for registered hunters',
        }
        
        created_categories = {}
        for name, desc in categories.items():
            cat, _ = ItemCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            created_categories[name] = cat
        return created_categories
    
    def create_entities(self, rank_prefix, min_level, max_level, count, categories):
        # Solo Leveling-inspired entities with proper categories
        rank_entities = {
            'E': [
                ("Giant Rat", ["Forest", "Swamp"], "Overgrown rodents with razor-sharp teeth"),
                ("Poison Toad", ["Swamp"], "Toxic amphibians that spit paralyzing venom"),
                ("Lesser Slime", ["Caverns", "Swamp"], "Semi-transparent gelatinous creatures"),
                ("Skeleton Grunt", ["Crypt", "Undead"], "Reanimated bones with rusty weapons"),
                ("Goblin Scout", ["Forest", "Ruins"], "Small humanoids that attack in packs"),
                ("Cave Bat", ["Caverns"], "Blind flying mammals with sonic screech"),
                ("Rotting Zombie", ["Crypt", "Undead"], "Slow-moving corpses that spread disease"),
                ("Thorn Bush", ["Forest"], "Animated plants that entangle prey"),
                ("Mud Elemental", ["Swamp"], "Living clay that suffocates victims"),
                ("Stone Crab", ["Caverns"], "Rock-shelled crustaceans with crushing claws"),
            ],
            'D': [
                ("Iron Golem", ["Foundry"], "Constructs of enchanted metal"),
                ("Ghoul", ["Crypt", "Undead"], "Flesh-eating undead with regenerative abilities"),
                ("Harpy", ["Sky Citadel"], "Winged humanoids that lure with song"),
                ("Basilisk", ["Caverns"], "Reptilian gaze that turns flesh to stone"),
                ("Fire Imp", ["Volcano"], "Small demons that throw magma bolts"),
                ("Treant Sapling", ["Forest"], "Young tree guardians that command vines"),
                ("Siren", ["Ocean"], "Aquatic beings that drown victims with illusions"),
                ("Wight", ["Crypt", "Undead"], "Spectral warriors that drain life force"),
                ("Giant Scorpion", ["Desert"], "Venomous arachnids with armored carapace"),
                ("Ice Sprite", ["Ice"], "Elemental spirits that freeze their surroundings"),
            ],
            'C': [
                ("Death Knight", ["Crypt", "Undead"], "Fallen warriors clad in dark armor"),
                ("Lava Elemental", ["Volcano"], "Living magma that incinerates foes"),
                ("Gargoyle Sentinel", ["Ruins", "Sky Citadel"], "Stone guardians that come to life at night"),
                ("Banshee", ["Ethereal", "Undead"], "Spectral beings whose wails shatter souls"),
                ("Chimera", ["Ruins", "Demon"], "Hybrid beasts with multiple animal heads"),
                ("Manticore", ["Desert", "Ruins"], "Lion-bodied creatures with scorpion tails"),
                ("Water Naga", ["Ocean", "Swamp"], "Serpentine beings that control water"),
                ("Earth Golem", ["Caverns", "Ruins"], "Massive stone constructs that cause earthquakes"),
                ("Frost Wyrm", ["Ice", "Caverns"], "Ice-breathing serpentine dragons"),
                ("Shadow Stalker", ["Ethereal", "Demon"], "Beings that move through darkness unseen"),
            ],
            'B': [
                ("Dragonkin Warrior", ["Dragonkin", "Volcano"], "Humanoid descendants of dragons"),
                ("Archmage Specter", ["Ethereal", "Ruins"], "Ghostly remnants of powerful spellcasters"),
                ("Behemoth", ["Ruins", "Dragonkin"], "Mountain-sized beasts that cause earthquakes"),
                ("Phoenix", ["Volcano", "Ethereal"], "Eternal firebirds that resurrect from ashes"),
                ("Thunderbird", ["Sky Citadel", "Ethereal"], "Giant birds that summon storms with their wings"),
                ("Abyssal Horror", ["Ocean", "Demon"], "Deep-sea creatures with tentacles and madness aura"),
                ("Ironclad Titan", ["Foundry", "Ruins"], "Massive war machines from a lost civilization"),
                ("Blizzard Elemental", ["Ice", "Ethereal"], "Living blizzards that freeze everything"),
                ("Sand King", ["Desert", "Dragonkin"], "Giant scorpion monarch that controls dunes"),
                ("Plague Doctor", ["Swamp", "Undead"], "Undead healers that spread disease instead of curing"),
            ],
            'A': [
                ("Ancient Dragon", ["Dragonkin", "Volcano"], "Millennia-old wyrms of immense power"),
                ("Lich Lord", ["Crypt", "Undead"], "Undead sorcerers who command legions of the dead"),
                ("Celestial Guardian", ["Sky Citadel", "Ethereal"], "Divine beings that protect sacred places"),
                ("Kraken", ["Ocean", "Demon"], "Colossal cephalopods that create whirlpools"),
                ("Infernal Duke", ["Demon", "Volcano"], "High-ranking demons from the fiery depths"),
                ("Frost Titan", ["Ice", "Ethereal"], "Giants who wield the power of eternal winter"),
                ("Time Weaver", ["Ethereal", "Ruins"], "Beings that manipulate the flow of time"),
                ("Nature Sovereign", ["Forest", "Ethereal"], "Spiritual embodiment of the natural world"),
                ("Soul Reaper", ["Undead", "Ethereal"], "Psychopomps that harvest souls of the dead"),
                ("Mecha-God", ["Foundry", "Ruins"], "Remnant of a hyper-advanced civilization"),
            ],
            'S': [
                ("Shadow Monarch", ["Ethereal", "Undead", "Demon"], "Ruler of darkness and death"),
                ("Dragon Emperor", ["Dragonkin", "Volcano", "Sky Citadel"], "Supreme ruler of all dragonkind"),
                ("Fallen Seraph", ["Sky Citadel", "Demon"], "Corrupted angels with broken wings"),
                ("Titan King", ["Ruins", "Ethereal"], "Ancestor of all giants wielding world-shaking power"),
                ("Abyss Lord", ["Ocean", "Demon", "Ethereal"], "Sovereign of the deepest, darkest ocean trenches"),
                ("Phoenix Monarch", ["Volcano", "Ethereal"], "King of the firebirds with eternal life"),
                ("Architect", ["Ruins", "Ethereal"], "Entity that designs reality itself"),
                ("Void Walker", ["Ethereal", "Demon"], "Being that exists between dimensions"),
                ("World Tree Guardian", ["Forest", "Ethereal"], "Protector of the cosmic tree of life"),
                ("Quantum Horror", ["Ethereal", "Demon"], "Creature that exists in multiple realities simultaneously"),
            ]
        }
        
        entities = rank_entities.get(rank_prefix, [])
        for i in range(count):
            if i < len(entities):
                name, cat_names, desc = entities[i]
            else:
                # Generate generic entities if not predefined
                name = f"{rank_prefix}-Rank Entity {i+1}"
                cat_names = random.sample(list(categories.keys()), random.randint(1, 2))
                desc = f"Powerful {rank_prefix}-Rank entity of {', '.join(cat_names)}"
            
            entity_type = random.choice(['minion', 'boss', 'final_boss'])
            if rank_prefix in ['SS', 'SSS', 'National']:
                entity_type = random.choice(['boss', 'final_boss'])
            
            level = random.randint(min_level, max_level)
            category_objs = [categories[cat] for cat in cat_names]
            
            entity, created = Entity.objects.get_or_create(
                name=name,
                defaults={
                    'entity_type': entity_type,
                    'description': desc,
                    'level': level,
                    'image_url': f"/entities/{slugify(name)}.png"
                }
            )
            
            if created:
                entity.categories.set(category_objs)
                self.stdout.write(f"Created {rank_prefix}-Rank entity: {name}")

    def create_dungeons(self, entity_categories, item_categories):
        dungeon_data = [
            # E-Rank Dungeons
            {
                "name": "E-Rank Whispering Forest",
                "rank": "E",
                "entity_categories": ["Forest"],
                "item_categories": ["Material", "Consumable"],
                "description": "A forest where the trees themselves whisper warnings to intruders",
                "min_floors": 3,
                "max_floors": 5,
                "min_time": 0.5,
                "max_time": 1,
                "base_xp": 2500, # 50 * 50
                "base_currency": 1000 # 20 * 50
            },
            {
                "name": "E-Rank Fetid Bog",
                "rank": "E",
                "entity_categories": ["Swamp"],
                "item_categories": ["Material", "Consumable"],
                "description": "Poisonous marshlands filled with toxic flora and fauna",
                "min_floors": 2,
                "max_floors": 4,
                "min_time": 0.4,
                "max_time": 0.8,
                "base_xp": 2250, # 45 * 50
                "base_currency": 900 # 18 * 50
            },
            
            # D-Rank Dungeons
            {
                "name": "D-Rank Sunken Crypt",
                "rank": "D",
                "entity_categories": ["Crypt", "Undead"],
                "item_categories": ["Core", "Material"],
                "description": "Flooded tombs where the dead refuse to rest peacefully",
                "min_floors": 4,
                "max_floors": 6,
                "min_time": 1,
                "max_time": 2,
                "base_xp": 7500, # 150 * 50
                "base_currency": 3750 # 75 * 50
            },
            {
                "name": "D-Rank Gloomy Caverns",
                "rank": "D",
                "entity_categories": ["Caverns"],
                "item_categories": ["Material", "Weapon"],
                "description": "Lightless tunnels where precious minerals drive miners mad",
                "min_floors": 3,
                "max_floors": 5,
                "min_time": 1.2,
                "max_time": 2.2,
                "base_xp": 8500, # 170 * 50
                "base_currency": 4250 # 85 * 50
            },
            
            # C-Rank Dungeons
            {
                "name": "C-Rank Clockwork Foundry",
                "rank": "C",
                "entity_categories": ["Foundry"],
                "item_categories": ["Core", "Armor"],
                "description": "An ancient factory still producing autonomous weapons",
                "min_floors": 5,
                "max_floors": 7,
                "min_time": 2,
                "max_time": 4,
                "base_xp": 20000, # 400 * 50
                "base_currency": 10000 # 200 * 50
            },
            {
                "name": "C-Rank Glimmer-Vein Caverns",
                "rank": "C",
                "entity_categories": ["Caverns"],
                "item_categories": ["Core", "Accessory"],
                "description": "Crystal-filled caves that amplify magical energies",
                "min_floors": 5,
                "max_floors": 8,
                "min_time": 2.5,
                "max_time": 4.5,
                "base_xp": 22500, # 450 * 50
                "base_currency": 11000 # 220 * 50
            },
            
            # B-Rank Dungeons
            {
                "name": "B-Rank Volcanic Lair",
                "rank": "B",
                "entity_categories": ["Volcano", "Dragonkin"],
                "item_categories": ["Artifact", "Weapon"],
                "description": "Molten tunnels deep within an active volcano",
                "min_floors": 6,
                "max_floors": 8,
                "min_time": 3,
                "max_time": 6,
                "base_xp": 40000, # 800 * 50
                "base_currency": 20000 # 400 * 50
            },
            {
                "name": "B-Rank Sky-High Aviary",
                "rank": "B",
                "entity_categories": ["Sky Citadel"],
                "item_categories": ["Accessory", "Skill Book"],
                "description": "Floating islands inhabited by winged beasts",
                "min_floors": 6,
                "max_floors": 9,
                "min_time": 4,
                "max_time": 7,
                "base_xp": 42500, # 850 * 50
                "base_currency": 21250 # 425 * 50
            },
            
            # A-Rank Dungeons
            {
                "name": "A-Rank Astral Prison",
                "rank": "A",
                "entity_categories": ["Ethereal", "Ruins"],
                "item_categories": ["Artifact", "Core"],
                "description": "Shattered dimension used to contain cosmic horrors",
                "min_floors": 7,
                "max_floors": 9,
                "min_time": 5,
                "max_time": 10,
                "base_xp": 75000, # 1500 * 50
                "base_currency": 37500 # 750 * 50
            },
            {
                "name": "A-Rank Abyssal Trench",
                "rank": "A",
                "entity_categories": ["Ocean", "Demon"],
                "item_categories": ["Artifact", "Accessory"],
                "description": "Deep-sea rift where light fears to tread",
                "min_floors": 8,
                "max_floors": 10,
                "min_time": 6,
                "max_time": 12,
                "base_xp": 80000, # 1600 * 50
                "base_currency": 40000 # 800 * 50
            },
            
            # S-Rank Dungeons
            {
                "name": "S-Rank Dragon's Graveyard",
                "rank": "S",
                "entity_categories": ["Ruins", "Dragonkin", "Undead"],
                "item_categories": ["Artifact", "Core"],
                "description": "Where ancient dragons come to die, their power animating their remains",
                "min_floors": 8,
                "max_floors": 12,
                "min_time": 8,
                "max_time": 16,
                "base_xp": 150000, # 3000 * 50
                "base_currency": 75000 # 1500 * 50
            },
            {
                "name": "S-Rank Demon King's Citadel",
                "rank": "S",
                "entity_categories": ["Demon", "Sky Citadel"],
                "item_categories": ["Artifact", "Weapon"],
                "description": "Floating fortress of the Demon King, protected by hellish legions",
                "min_floors": 10,
                "max_floors": 15,
                "min_time": 12,
                "max_time": 24,
                "base_xp": 175000, # 3500 * 50
                "base_currency": 90000 # 1800 * 50
            },

            # SS-Rank Dungeons
            {
                "name": "SS-Rank Void Nexus",
                "rank": "SS",
                "entity_categories": ["Ethereal", "Demon"],
                "item_categories": ["Artifact", "Core"],
                "description": "A tear in reality leading to a realm of endless chaos.",
                "min_floors": 12,
                "max_floors": 18,
                "min_time": 18,
                "max_time": 36,
                "base_xp": 250000,
                "base_currency": 125000
            },

            # SSS-Rank Dungeons
            {
                "name": "SSS-Rank World Tree",
                "rank": "SSS",
                "entity_categories": ["Forest", "Ethereal"],
                "item_categories": ["Artifact", "Skill Book"],
                "description": "The heart of the world, where cosmic guardians reside.",
                "min_floors": 15,
                "max_floors": 20,
                "min_time": 24,
                "max_time": 48,
                "base_xp": 500000,
                "base_currency": 250000
            },

            # National-Rank Dungeons
            {
                "name": "National-Rank Dimensional Rift",
                "rank": "National",
                "entity_categories": ["Ethereal", "Demon", "Undead"],
                "item_categories": ["Artifact", "Core", "Weapon"],
                "description": "A gateway to other worlds, unleashing unstoppable horrors.",
                "min_floors": 20,
                "max_floors": 25,
                "min_time": 48,
                "max_time": 96,
                "base_xp": 1000000,
                "base_currency": 500000
            }
        ]
        
        for data in dungeon_data:
            entity_cat_objs = [entity_categories[cat] for cat in data['entity_categories']]
            item_cat_objs = [item_categories[cat] for cat in data['item_categories']]
            
            dungeon, created = Dungeon.objects.get_or_create(
                name=data['name'],
                defaults={
                    'rank': data['rank'],
                    'description': data['description'],
                    'min_floors': data['min_floors'],
                    'max_floors': data['max_floors'],
                    'min_total_time_hours': data['min_time'],
                    'max_total_time_hours': data['max_time'],
                    'base_xp': data['base_xp'],
                    'base_currency': data['base_currency'],
                    'is_active': True
                }
            )
            
            if created:
                # Set entity categories (which entities can appear)
                dungeon.entity_categories.set(entity_cat_objs)
                # Set item categories (which items can drop)
                dungeon.item_categories.set(item_cat_objs)
                self.stdout.write(f"Created dungeon: {data['name']}")