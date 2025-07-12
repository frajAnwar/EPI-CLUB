
import random
from django.db import transaction
from .models import Entity
from items.models import Item, InventoryItem
from accounts.models import User, Currency, UserCurrency

class LootService:

    @staticmethod
    @transaction.atomic
    def add_item_to_inventory(user: User, item: Item, quantity: int = 1, metadata: dict = None):
        """
        Adds an item to a user's inventory. 
        If the item is stackable, it increases the quantity of an existing stack.
        If it's not stackable, it creates a new unique instance.
        """
        if not isinstance(item, Item):
            raise TypeError("Provided item must be an instance of the Item model.")

        if item.is_stackable:
            inventory_item, created = InventoryItem.objects.get_or_create(
                user=user,
                item=item,
                # We assume stackable items don't have unique metadata that needs matching
                defaults={'quantity': quantity, 'metadata': metadata or {}}
            )

            if not created:
                inventory_item.quantity += quantity
                inventory_item.save()
            return inventory_item
        else:
            # For non-stackable items, always create a new row
            inventory_item = InventoryItem.objects.create(
                user=user,
                item=item,
                quantity=1, # Non-stackable items always have a quantity of 1
                metadata=metadata or {}
            )
            return inventory_item

    @staticmethod
    @transaction.atomic
    def add_currency(user: User, amount: int, currency_code: str = 'GAME_COIN'):
        """
        Adds a specified amount of a currency to the user's account using the
        correct UserCurrency model. This operation is atomic.
        """
        if amount <= 0:
            return

        try:
            # Use get_or_create for robustness, especially in development.
            currency, _ = Currency.objects.get_or_create(code=currency_code.upper())
            
            user_currency, created = UserCurrency.objects.get_or_create(
                user=user,
                currency=currency,
                defaults={'balance': 0}
            )
            
            user_currency.balance += amount
            user_currency.save()

        except Currency.DoesNotExist:
            # This case should ideally not be hit if currencies are pre-populated.
            raise ValueError(f"Currency with code {currency_code} does not exist. Please create it in the admin panel.")
   
    RARITY_CHANCES = {
        'E': {'common': 0.696, 'uncommon': 0.199, 'rare': 0.060, 'epic': 0.020,'legendary': 0.010, 'mythic': 0.005, 'relic': 0.003, 'masterwork': 0.001, 'eternal': 0.001},
        'D': {'common': 0.592, 'uncommon': 0.217, 'rare': 0.079, 'epic': 0.039,'legendary': 0.020, 'mythic': 0.010, 'relic': 0.005, 'masterwork': 0.003, 'eternal': 0.002},
        'C': {'common': 0.000, 'uncommon': 0.348, 'rare': 0.248, 'epic': 0.178,'legendary': 0.099, 'mythic': 0.059, 'relic': 0.030, 'masterwork': 0.020, 'eternal': 0.004},
        'B': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.298, 'epic': 0.248,'legendary': 0.179, 'mythic': 0.099, 'relic': 0.069, 'masterwork': 0.060, 'eternal': 0.006},
        'A': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.277, 'epic': 0.257,'legendary': 0.178, 'mythic': 0.099, 'relic': 0.079, 'masterwork': 0.059, 'eternal': 0.010},
        'S': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.000, 'epic': 0.361,'legendary': 0.309, 'mythic': 0.155, 'relic': 0.083, 'masterwork': 0.062, 'eternal': 0.030},
        'SS': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.000, 'epic': 0.357,'legendary': 0.306, 'mythic': 0.153, 'relic': 0.082, 'masterwork': 0.053, 'eternal': 0.050},
        'SSS': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.000, 'epic': 0.000,'legendary': 0.389, 'mythic': 0.268, 'relic': 0.154, 'masterwork': 0.119, 'eternal': 0.070},
        'National': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.000, 'epic': 0.000,'legendary': 0.270, 'mythic': 0.280, 'relic': 0.180, 'masterwork': 0.160, 'eternal': 0.110},
    }

    GUARDIAN_RARITY_CHANCES = {
        'E': {'common': 0.496, 'uncommon': 0.299, 'rare': 0.120, 'epic': 0.050,'legendary': 0.020, 'mythic': 0.010, 'relic': 0.005, 'masterwork': 0.003, 'eternal': 0.002},
        'D': {'common': 0.392, 'uncommon': 0.317, 'rare': 0.159, 'epic': 0.059,'legendary': 0.030, 'mythic': 0.015, 'relic': 0.008, 'masterwork': 0.005, 'eternal': 0.003},
        'C': {'common': 0.000, 'uncommon': 0.248, 'rare': 0.320, 'epic': 0.178,'legendary': 0.109, 'mythic': 0.069, 'relic': 0.038, 'masterwork': 0.030, 'eternal': 0.007},
        'B': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.398, 'epic': 0.298,'legendary': 0.129, 'mythic': 0.079, 'relic': 0.049, 'masterwork': 0.030, 'eternal': 0.010},
        'A': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.377, 'epic': 0.307,'legendary': 0.128, 'mythic': 0.079, 'relic': 0.059, 'masterwork': 0.039, 'eternal': 0.015},
        'S': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.000, 'epic': 0.461,'legendary': 0.259, 'mythic': 0.125, 'relic': 0.063, 'masterwork': 0.052, 'eternal': 0.040},
        'SS': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.000, 'epic': 0.261,'legendary': 0.336, 'mythic': 0.168, 'relic': 0.097, 'masterwork': 0.075, 'eternal': 0.063},
        'SSS': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.000, 'epic': 0.000,'legendary': 0.250, 'mythic': 0.320, 'relic': 0.200, 'masterwork': 0.120, 'eternal': 0.110},
        'National': {'common': 0.000, 'uncommon': 0.000, 'rare': 0.000, 'epic': 0.000,'legendary': 0.200, 'mythic': 0.300, 'relic': 0.200, 'masterwork': 0.180, 'eternal': 0.120},
    }

    RARITY_ORDER = ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic', 'relic', 'masterwork', 'eternal']

    @staticmethod
    def generate_loot(entity: Entity):
        is_guardian = entity.entity_type == 'final_boss'
        xp_multiplier = 2 if is_guardian else 1
        coin_multiplier = 2 if is_guardian else 1
        xp = random.randint(entity.min_xp, entity.max_xp) * xp_multiplier
        coins = random.randint(entity.min_coins, entity.max_coins) * coin_multiplier

        rewards = {
            'xp': xp,
            'coins': coins,
            'items': []
        }

        possible_items_pool = list(Item.objects.filter(categories__in=entity.loot_categories.all()).distinct())
        if not possible_items_pool:
            return rewards

        num_drops = random.randint(1, 2) if is_guardian else 1
        rarity_table = LootService.GUARDIAN_RARITY_CHANCES if is_guardian else LootService.RARITY_CHANCES

        for _ in range(num_drops):
            rank_chances = rarity_table.get(entity.rank, rarity_table['E'])
            rarity_roll = random.random()
            chosen_rarity = 'common'
            cumulative_chance = 0
            for rarity, chance in rank_chances.items():
                cumulative_chance += chance
                if rarity_roll < cumulative_chance:
                    chosen_rarity = rarity
                    break

            # --- Intelligent Fallback Logic 2.0 ---
            item_to_award = None
            rarity_index = LootService.RARITY_ORDER.index(chosen_rarity)

            # 1. Search down from the chosen rarity
            for i in range(rarity_index, -1, -1):
                fallback_rarity = LootService.RARITY_ORDER[i]
                items_of_rarity = [item for item in possible_items_pool if item.rarity == fallback_rarity]
                if items_of_rarity:
                    item_to_award = random.choice(items_of_rarity)
                    break
            
            # 2. If no item was found, search up from the chosen rarity
            if not item_to_award:
                for i in range(rarity_index + 1, len(LootService.RARITY_ORDER) - 1):
                    fallback_rarity = LootService.RARITY_ORDER[i]
                    items_of_rarity = [item for item in possible_items_pool if item.rarity == fallback_rarity]
                    if items_of_rarity:
                        item_to_award = random.choice(items_of_rarity)
                        break

            if item_to_award:
                rewards['items'].append({'item_id': item_to_award.id, 'quantity': 1})

        return rewards

    @staticmethod
    def calculate_floor_rewards(floor_log):
        total_xp = 0
        total_coins = 0
        items_found = []

        for encounter in floor_log['encounters']:
            result = encounter.get('result', {})
            if result.get('outcome') == 'success':
                loot = result.get('loot', {})
                total_xp += loot.get('xp', 0)
                total_coins += loot.get('coins', 0)
                items_found.extend(loot.get('items', []))
        
        return {
            'xp': total_xp,
            'coins': total_coins,
            'items': items_found
        }
