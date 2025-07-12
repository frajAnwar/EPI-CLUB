# items/management/commands/seed_items.py
from django.core.management.base import BaseCommand
from items.models import Item, ItemCategory, Currency
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = 'Seeds the database with Solo Leveling-inspired items and currencies'

    def handle(self, *args, **options):
        self.stdout.write('Seeding the world with magical items...')
        
        # Create or get categories
        categories = self.create_categories()
        
        # Create currencies
        self.create_currencies()
        
        # Create items for each rarity
        self.create_items('common', 50, categories)
        self.create_items('uncommon', 40, categories)
        self.create_items('rare', 30, categories)
        self.create_items('epic', 25, categories)
        self.create_items('legendary', 20, categories)
        self.create_items('mythic', 15, categories)
        self.create_items('relic', 10, categories)
        self.create_items('masterwork', 8, categories)
        self.create_items('eternal', 5, categories)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded the world with magical items!'))
    
    def create_categories(self):
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
    
    def create_currencies(self):
        currencies = [
            ('Gold', 'Basic currency for transactions', 'G', 1.0),
            ('Mana Shards', 'Crystallized magical energy', 'MS', 10.0),
            ('Hunter Points', 'Special currency for hunter association', 'HP', 100.0),
            ('Dragon Scales', 'Rare currency from dragonkin', 'DS', 1000.0),
            ('Eternal Essence', 'Divine fragments from god-like beings', 'EE', 10000.0),
        ]
        
        for name, desc, code, exchange_rate in currencies:
            Currency.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': desc,
                    'exchange_rate': exchange_rate
                }
            )
    
    def create_items(self, rarity, count, categories):
        # Predefined items with Solo Leveling inspiration
        predefined_items = {
            'common': [
                ("Health Potion", "Consumable", "Restores 50 HP. Basic red potion."),
                ("Mana Elixir", "Consumable", "Restores 30 MP. Blue glowing liquid."),
                ("Iron Dagger", "Weapon", "Basic starter weapon for novice hunters."),
                ("Leather Armor", "Armor", "Simple protection made from monster hide."),
                ("Wooden Shield", "Armor", "Lightweight defense for beginners."),
                ("Apprentice Gloves", "Accessory", "Slightly enhances magic control."),
                ("Monster Fang", "Material", "Common crafting component from E-rank beasts."),
                ("Basic Healing Scroll", "Skill Book", "Teaches minor healing spell."),
                ("Torch", "Accessory", "Lights dark dungeon corridors."),
                ("Rope", "Material", "Essential dungeon exploration tool."),
            ],
            'uncommon': [
                ("Steel Sword", "Weapon", "Well-balanced weapon for D-rank hunters."),
                ("Chainmail", "Armor", "Interlocking metal rings provide good protection."),
                ("Amulet of Vigor", "Accessory", "Slightly boosts stamina recovery."),
                ("Greater Health Potion", "Consumable", "Restores 150 HP. More potent version."),
                ("Goblin Core", "Core", "Energy source from goblin-type monsters."),
                ("Shadow Cloak", "Armor", "Reduces visibility in dark environments."),
                ("Fireball Tome", "Skill Book", "Teaches basic fire magic attack."),
                ("Antidote", "Consumable", "Cures poison from swamp creatures."),
                ("Silver Arrowheads", "Material", "Crafted projectiles effective against undead."),
                ("Hunter's Compass", "Accessory", "Points toward nearest dungeon entrance."),
            ],
            'rare': [
                ("Mithril Blade", "Weapon", "Lightweight yet incredibly sharp weapon."),
                ("Dragonhide Armor", "Armor", "Crafted from young dragon scales."),
                ("Ring of Shadows", "Accessory", "Enhances stealth capabilities."),
                ("Elixir of Strength", "Consumable", "Temporarily boosts physical damage."),
                ("S-Rank Gate Fragment", "Dungeon Key", "Opens unstable high-rank gates."),
                ("Ice Wyvern Core", "Core", "Frozen essence from ice-based dragons."),
                ("Double Jump Boots", "Accessory", "Allows mid-air jump maneuver."),
                ("Teleport Scroll", "Skill Book", "Teaches short-range teleportation."),
                ("Phoenix Feather", "Material", "Rare drop from fire-attribute birds."),
                ("Night Vision Goggles", "Accessory", "See clearly in complete darkness."),
            ],
            'epic': [
                ("Demon Slayer Sword", "Weapon", "Glows red in presence of demonic beings."),
                ("Orichalcum Plate", "Armor", "Legendary metal that deflects magic."),
                ("Amulet of the Monarch", "Accessory", "Greatly boosts mana regeneration."),
                ("Elixir of Immortality", "Consumable", "Prevents death once per dungeon run."),
                ("Dragon Heart Core", "Core", "Pulsating heart of an adult dragon."),
                ("Gate Master Key", "Dungeon Key", "Opens any A-rank or lower gate."),
                ("Shadow Exchange Manual", "Skill Book", "Teaches advanced teleportation skill."),
                ("Frostfire Gauntlets", "Armor", "Allows casting of ice and fire spells."),
                ("Sung Jin-Woo's Dagger", "Weapon", "Replica of the Shadow Monarch's weapon."),
                ("Architect's Blueprint", "Artifact", "Reveals dungeon layouts and secrets."),
            ],
            'legendary': [
                ("Heavenly Sword", "Weapon", "Blade blessed by celestial beings."),
                ("Armor of the Monarch", "Armor", "Legendary armor worn by past Shadow Monarchs."),
                ("Crown of Dominance", "Accessory", "Enhances control over summoned creatures."),
                ("Potion of Awakening", "Consumable", "Grants temporary S-rank powers."),
                ("Ant King's Core", "Core", "Essence from an insectoid monarch."),
                ("Red Gate Key", "Dungeon Key", "Opens the deadly double-dungeon gates."),
                ("Ruler's Authority", "Skill Book", "Teaches domain control skill."),
                ("Igris's Helm", "Armor", "Helmet worn by the Shadow Monarch's knight."),
                ("Kamish's Fang", "Weapon", "Weapon crafted from the deadliest dragon."),
                ("Chalice of Rebirth", "Artifact", "Allows one resurrection per month."),
            ],
            'mythic': [
                ("Shadow Sovereign's Blade", "Weapon", "Weapon that channels absolute darkness."),
                ("Armor of Absolute Void", "Armor", "Armor that absorbs all light around it."),
                ("Ring of System", "Accessory", "Mysterious ring that enhances all stats."),
                ("Elixir of Eternal Shadow", "Consumable", "Grants permanent shadow affinity."),
                ("Fragmented Monarch Crystal", "Core", "Shard from the Shadow Monarch's power."),
                ("Jeju Island Gate Key", "Dungeon Key", "Opens gates to the deadly island dungeon."),
                ("Army of the Dead Tome", "Skill Book", "Teaches mass shadow soldier summoning."),
                ("Dragon Emperor's Scale", "Material", "Scale from the ruler of all dragons."),
                ("Hourglass of Chronos", "Artifact", "Can manipulate time within dungeons."),
                ("Sovereign's Mantle", "Armor", "Cloak that transforms into shadow wings."),
            ],
            'relic': [
                ("Spear of Longinus", "Weapon", "Weapon that can kill immortal beings."),
                ("Shield of Atlas", "Armor", "Can withstand continental-level attacks."),
                ("Crown of the Shadow Monarch", "Accessory", "Final symbol of the Shadow Sovereign."),
                ("Ambrosia", "Consumable", "Nectar of gods that grants permanent stat boosts."),
                ("World Tree Seed", "Material", "Can grow into a dimensional anchor point."),
                ("Tower Key", "Dungeon Key", "Opens gates to the System's challenge tower."),
                ("Omniscient Eye", "Artifact", "Reveals all truths about dungeons and monsters."),
                ("Sovereign's Sigil", "Accessory", "Mark of authority over all shadows."),
                ("Heart of the World", "Core", "The core energy of a planet's life force."),
                ("Ragnarök Trigger", "Artifact", "Can initiate a dungeon apocalypse event."),
            ],
            'masterwork': [
                ("Absolute Being's Finger", "Weapon", "Fragment of the creator's power."),
                ("Void-walker Cloak", "Armor", "Allows travel between dimensions."),
                ("System Core Fragment", "Core", "Piece of the mysterious System's origin."),
                ("Sovereign's Command", "Skill Book", "Teaches reality-altering commands."),
                ("Dragon Monarch's Horn", "Material", "Material stronger than adamantium."),
                ("Golden Key", "Dungeon Key", "Opens gates to the creator's realm."),
                ("Infinity Gauntlet", "Accessory", "Channels unlimited elemental power."),
                ("Eternity Vessel", "Consumable", "Stores unlimited mana for one use."),
                ("Singularity Focus", "Artifact", "Creates black holes as weapons."),
                ("Monarch's Legacy", "Accessory", "Contains the combined wisdom of all monarchs."),
            ],
            'eternal': [
                ("The Architect's Pen", "Weapon", "Can rewrite dungeon rules and reality."),
                ("Armor of Finality", "Armor", "Makes wearer immune to all damage types."),
                ("Essence of the System", "Core", "The complete source of the Hunter System."),
                ("Codex of Creation", "Skill Book", "Teaches world-creation magic."),
                ("Key of Omnipotence", "Dungeon Key", "Opens any gate across all dimensions."),
            ]
        }
        
        items = predefined_items.get(rarity, [])
        if len(items) < count:
            # Generate additional generic items
            for i in range(count - len(items)):
                item_type = random.choice(list(categories.keys()))
                name = f"{rarity.capitalize()} {item_type} {i+1}"
                desc = f"Powerful {rarity} {item_type} for elite hunters"
                items.append((name, item_type, desc))
        
        for name, cat_name, desc in items:
            # Get random categories
            category = categories[cat_name]
            additional_cats = random.sample(
                list(categories.values()), 
                k=random.randint(1, 2)
            )
            all_cats = [category] + additional_cats
            
            # Determine item value based on rarity
            value = {
                'common': random.randint(1, 10),
                'uncommon': random.randint(10, 50),
                'rare': random.randint(50, 200),
                'epic': random.randint(200, 1000),
                'legendary': random.randint(1000, 5000),
                'mythic': random.randint(5000, 20000),
                'relic': random.randint(20000, 100000),
                'masterwork': random.randint(100000, 500000),
                'eternal': random.randint(500000, 1000000),
            }[rarity]
            
            item, created = Item.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'rarity': rarity,
                    'value': value,
                    'image_url': f"/items/{slugify(name)}.png",
                    'stackable': cat_name in ['Consumable', 'Material'],
                    'max_stack': 99 if cat_name in ['Consumable', 'Material'] else 1
                }
            )
            
            if created:
                item.categories.set(list(set(all_cats)))
                self.stdout.write(f"Created {rarity} item: {name}")

# Add this to items/models.py if not already present
class Currency(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    exchange_rate = models.FloatField(
        default=1.0, 
        help_text="Value relative to base currency"
    )
    icon = models.ImageField(
        upload_to='currency_icons/', 
        blank=True, 
        null=True
    )
    
    def __str__(self):
        return f"{self.name} ({self.code})"