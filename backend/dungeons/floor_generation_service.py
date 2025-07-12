
import random
from dungeons.models import Entity, TacticalApproach

class FloorGenerationService:
    RANK_HIERARCHY = ['E', 'D', 'C', 'B', 'A', 'S', 'SS', 'SSS', 'National']
    RANK_BUDGETS = {
        'E': 16, 'D': 50, 'C': 80, 'B': 120, 'A': 180, 
        'S': 250, 'SS': 350, 'SSS': 500, 'National': 1000
    }

    @staticmethod
    def _get_random_entity(rank, entity_type, max_power=None):
        """Fetches a random entity of a specific rank and type, with an optional power cap."""
        query = Entity.objects.filter(rank=rank, entity_type=entity_type)
        if max_power:
            query = query.filter(power__lte=max_power)
        
        entity = query.order_by('?').first()
        return entity

    @staticmethod
    def _calculate_budget(dungeon_rank, total_floors, current_floor):
        """Calculates a power budget based on dungeon rank and floor progression."""
        # Get the base budget for the dungeon's rank, with a fallback for safety.
        base_budget = FloorGenerationService.RANK_BUDGETS.get(dungeon_rank, 50)
        
        # The progression acts as a multiplier on the rank-specific base budget.
        # Example for a 10-floor dungeon:
        # Floor 1: 1.1x multiplier
        # Floor 5: 1.5x multiplier
        # Floor 10: 2.0x multiplier
        floor_multiplier = 1 + (current_floor / total_floors)*1.5
        
        budget = base_budget * floor_multiplier
        return int(budget)

    @staticmethod
    def generate_floor(dungeon, total_floors, current_floor):
        budget = FloorGenerationService._calculate_budget(dungeon.rank, total_floors, current_floor)
        thematic_entities = Entity.objects.filter(categories__in=dungeon.entity_categories.all())
        final_entities = []

        is_final_floor = current_floor == total_floors
        is_mid_boss_floor = not is_final_floor and current_floor == total_floors // 2

        if is_final_floor:
            # Final floor MUST be a final_boss
            boss = thematic_entities.filter(entity_type='final_boss', rank=dungeon.rank).order_by('-power').first()
            if boss:
                final_entities.append({'entity_id': boss.id, 'name': boss.name, 'power': boss.power})
        elif is_mid_boss_floor:
            # Mid-boss floor is guaranteed to be a boss
            boss = FloorGenerationService._find_suitable_boss(budget, thematic_entities.filter(entity_type='boss', rank=dungeon.rank))
            if boss:
                final_entities.append({'entity_id': boss.id, 'name': boss.name, 'power': boss.power})
        else:
            # Regular floors have a chance for a boss, otherwise a squad
            if random.random() < 0.40:
                boss = FloorGenerationService._find_suitable_boss(budget, thematic_entities.filter(entity_type='boss', rank=dungeon.rank))
                if boss:
                    final_entities.append({'entity_id': boss.id, 'name': boss.name, 'power': boss.power})
        
        # If no boss was placed (and it wasn't a required boss floor), build a squad
        if not final_entities:
            dungeon_rank_index = FloorGenerationService.RANK_HIERARCHY.index(dungeon.rank)
            allowed_rank_indices = range(max(0, dungeon_rank_index - 1), dungeon_rank_index + 1)
            allowed_ranks = [FloorGenerationService.RANK_HIERARCHY[i] for i in allowed_rank_indices]
            squad_pool = thematic_entities.filter(entity_type='minion', rank__in=allowed_ranks)
            if squad_pool.exists():
                final_entities = FloorGenerationService._build_squad(budget, squad_pool)

        if not final_entities:
            raise Exception(f"CRITICAL ERROR: Could not populate floor for dungeon '{dungeon.name}'. No suitable entities found for budget {budget}.")

        total_power = sum(entity['power'] for entity in final_entities)
        encounters = [{
            'entities': final_entities,
            'total_power': total_power
        }]

        # Generate tactical approaches
        distinct_categories = TacticalApproach.objects.values_list('category', flat=True).distinct()
        random_categories = random.sample(list(distinct_categories), min(len(distinct_categories), 3))

        tactical_choices = []
        for category in random_categories:
            approach = TacticalApproach.objects.filter(category=category).order_by('?').first()
            if approach:
                tactical_choices.append({'id': approach.id, 'name': approach.name, 'description': approach.description})

        # Fallback if we still don't have enough choices
        if len(tactical_choices) < 3:
            existing_ids = {tc['id'] for tc in tactical_choices}
            remaining_needed = 3 - len(tactical_choices)
            fallback_choices = TacticalApproach.objects.exclude(id__in=existing_ids).order_by('?')[:remaining_needed]
            for ta in fallback_choices:
                 tactical_choices.append({'id': ta.id, 'name': ta.name, 'description': ta.description})

        return {
            'encounters': encounters,
            'tactical_approaches': tactical_choices
        }

    @staticmethod
    def _find_suitable_boss(budget, pool):
        # Try to find a boss that fits the budget, starting from the most powerful
        boss = pool.filter(power__lte=budget).order_by('-power').first()
        if not boss:
            # If no boss fits, find the closest one below the budget from any lower rank
            boss = Entity.objects.filter(entity_type='boss', power__lte=budget).order_by('-power').first()
        return boss

    @staticmethod
    def _build_squad(budget, pool):
        """Builds a varied squad of minions by spending a power budget."""
        squad = []
        current_budget = budget
        min_budget_spend = budget * 0.6
        max_squad_size = 5

        possible_minions = list(pool.filter(power__lte=current_budget).order_by('-power'))

        if not possible_minions:
            return []

        while len(squad) < max_squad_size and current_budget > 0:
            suitable_minions = [m for m in possible_minions if m.power <= current_budget and m.power > 0]
            if not suitable_minions:
                break

            minion_to_add = random.choice(suitable_minions)

            squad.append({
                'entity_id': minion_to_add.id,
                'name': minion_to_add.name,
                'power': minion_to_add.power
            })
            current_budget -= minion_to_add.power

            if (budget - current_budget) >= min_budget_spend and squad:
                break

        return squad
