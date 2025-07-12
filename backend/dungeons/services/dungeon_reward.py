import random
from items.models import Item
from transactions.services import atomic_item_currency_transfer

class DungeonRewardService:
    def __init__(self, user, dungeon_run):
        self.user = user
        self.dungeon_run = dungeon_run

    def calculate_rewards(self):
        rewards = {
            'xp': self.dungeon_run.dungeon.base_xp,
            'game_coin': self.dungeon_run.dungeon.base_currency,
            'items': []
        }

        # Roll for item drop
        for rarity, drop_rate in self.dungeon_run.dungeon.rarity_drop_rates.items():
            if random.random() < self.apply_modifiers(drop_rate):
                item = self.get_random_item(rarity)
                if item:
                    rewards['items'].append(item)
                break
        
        return rewards

    def apply_modifiers(self, base_rate):
        # Placeholder: Apply talent and dungeon state modifiers
        return base_rate

    def get_random_item(self, rarity):
        item_categories = self.dungeon_run.dungeon.item_categories.all()
        items = Item.objects.filter(rarity=rarity, category__in=item_categories)
        if items.exists():
            return random.choice(items)
        return None

    def distribute_rewards(self, rewards):
        # Grant XP
        self.user.xp += rewards['xp']
        self.user.save()

        # Grant GameCoin
        atomic_item_currency_transfer(
            user=self.user,
            item=None,
            item_delta=0,
            currency='game',
            currency_delta=rewards['game_coin'],
            action='dungeon_reward',
            source='dungeon_run',
            metadata={'dungeon_run_id': self.dungeon_run.id}
        )

        # Grant items
        for item in rewards['items']:
            atomic_item_currency_transfer(
                user=self.user,
                item=item,
                item_delta=1,
                currency=None,
                currency_delta=0,
                action='dungeon_reward',
                source='dungeon_run',
                metadata={'dungeon_run_id': self.dungeon_run.id}
            )
