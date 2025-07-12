import random
from django.db import transaction
from django.db.models import F
from accounts.models import UserCurrency, Currency

from .loot_services import LootService

def grant_dungeon_rewards(user, dungeon_run, encounter_type, entity_id=None):
    rewards = {}
    entity = None
    if entity_id:
        entity = Entity.objects.get(id=entity_id)

    # 1. Grant GameCoin
    base_coin = 0
    if encounter_type == 'minion':
        base_coin = 5
    elif encounter_type == 'floor_guardian':
        base_coin = 25
    elif encounter_type == 'gate_completion':
        base_coin = 100
    
    if entity:
        coin_reward = int(base_coin * (1 + entity.power / 100))
        rewards['game_coin'] = coin_reward
        with transaction.atomic():
            game_currency = Currency.objects.get(code='game')
            currency, _ = UserCurrency.objects.get_or_create(user=user, currency=game_currency)
            currency.balance = F('balance') + coin_reward
            currency.save()

    # 2. Grant XP
    base_xp = 0
    if encounter_type == 'floor_guardian':
        base_xp = 50
    elif encounter_type == 'gate_completion':
        base_xp = 250

    if entity:
        xp_reward = int(base_xp * (1 + entity.power / 100))
        rewards['xp'] = xp_reward
        from accounts.leveling_services import LevelingService
        LevelingService.grant_xp(user, xp_reward)

    # 3. Generate Loot
    if entity_id:
        entity = Entity.objects.get(id=entity_id)
        item = LootService.generate_loot(dungeon_run.dungeon, entity)
        if item:
            rewards['item'] = {'id': item.id, 'name': item.name}
            # In a real implementation, you would add the item to the player's inventory here

    # 4. Gate Completion Chest
    if encounter_type == 'gate_completion':
        rewards['gate_chest'] = True

    # Append rewards to the dungeon run log
    dungeon_run.rewards.append(rewards)
    dungeon_run.save()

    return rewards
