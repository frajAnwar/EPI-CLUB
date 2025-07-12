
from django.core.management.base import BaseCommand
from dungeons.models import Entity

class Command(BaseCommand):
    help = "Rebalances the XP and coin rewards for all entities based on their rank and type."

    # Base XP values for each rank
    BASE_XP = {
        'E': 40, 'D': 120, 'C': 300, 'B': 600, 'A': 1000,
        'S': 1800, 'SS': 2800, 'SSS': 4500, 'National': 8000
    }

    # Base coin values, boosted
    BASE_COINS = {
        'E': 200, 'D': 800, 'C': 2000, 'B': 4500, 'A': 8000,
        'S': 15000, 'SS': 25000, 'SSS': 40000, 'National': 70000
    }

    # Multipliers for entity types
    TYPE_MULTIPLIERS = {
        'minion': 1.0,
        'boss': 5.0,
        'final_boss': 15.0,
    }

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting entity rebalance..."))
        
        updated_count = 0
        for entity in Entity.objects.all():
            base_xp = self.BASE_XP.get(entity.rank, 20)
            base_coins = self.BASE_COINS.get(entity.rank, 10)
            multiplier = self.TYPE_MULTIPLIERS.get(entity.entity_type, 1.0)

            final_xp = base_xp * multiplier
            final_coins = base_coins * multiplier

            entity.min_xp = int(final_xp * 0.9)
            entity.max_xp = int(final_xp * 1.1)
            entity.min_coins = int(final_coins * 0.9)
            entity.max_coins = int(final_coins * 1.1)

            entity.save()
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully rebalanced {updated_count} entities."))
