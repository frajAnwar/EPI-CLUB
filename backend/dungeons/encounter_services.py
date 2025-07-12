import random
from dungeons.models import Entity, DungeonRun, TacticalApproach

class EncounterService:
    @staticmethod
    def generate_floor_plan(dungeon_run: DungeonRun):
        dungeon = dungeon_run.dungeon
        rank = dungeon.rank

        floor_plan = []

        # Query for entities that match the dungeon's rank and categories
        possible_entities = Entity.objects.filter(
            rank=rank,
            categories__in=dungeon.entity_categories.all()
        ).distinct()

        minions = possible_entities.filter(entity_type='minion')
        guardians = possible_entities.filter(entity_type='boss')
        final_bosses = possible_entities.filter(entity_type='final_boss')

        if not minions.exists() or not guardians.exists():
            # If no entities for this rank, the floor plan will be empty
            return []

        possible_approaches = list(TacticalApproach.objects.all())

        for i in range(dungeon_run.total_floors):
            is_final_floor = (i + 1) == dungeon_run.total_floors

            # 1. Generate encounters for the floor
            num_encounters = random.randint(3, 5) # A reasonable default
            floor_encounters = []
            for _ in range(num_encounters):
                entity = minions.order_by('?').first()
                floor_encounters.append({
                    "entity_id": entity.id,
                    "name": f"{entity.name} ({entity.rank})",
                    "power": entity.power
                })

            # 2. Select a Floor Guardian or Final Boss
            if is_final_floor and final_bosses.exists():
                guardian_entity = final_bosses.order_by('?').first()
            else:
                guardian_entity = guardians.order_by('?').first()

            floor_guardian = {
                "name": f"{guardian_entity.name} ({guardian_entity.rank})",
                "power": guardian_entity.power
            }

            # 3. Select diverse Tactical Approaches for the *next* floor
            next_floor_approaches = []
            if not is_final_floor:
                categorized_approaches = {}
                for approach in possible_approaches:
                    categorized_approaches.setdefault(approach.category, []).append(approach)
                
                chosen_categories = random.sample(list(categorized_approaches.keys()), k=min(3, len(categorized_approaches)))
                for category in chosen_categories:
                    approach_obj = random.choice(categorized_approaches[category])
                    next_floor_approaches.append({
                        "id": approach_obj.id,
                        "name": approach_obj.name,
                        "description": approach_obj.description,
                        "category": approach_obj.category,
                        "effects": approach_obj.effects,
                    })

            floor_plan.append({
                "floor": i + 1,
                "encounters": floor_encounters,
                "floor_guardian": floor_guardian,
                "tactical_approaches": next_floor_approaches
            })
            
        return floor_plan

    @staticmethod
    def calculate_success_chance(player_power, encounter_power):
        import math
        power_difference = player_power - encounter_power
        
        # The 'k' value controls the steepness of the curve.
        # A lower k makes the curve steeper (more punishing/rewarding).
        k = 0.08 
        
        # Sigmoid function: 1 / (1 + e^(-k * x))
        # We multiply by 100 to get a percentage.
        chance = 100 / (1 + math.exp(-k * power_difference))
        
        # Clamp the result to ensure it's never 0 or 100.
        return max(1, min(99, chance))

    @staticmethod
    def resolve_encounter(player_power, encounter_power):
        success_chance = EncounterService.calculate_success_chance(player_power, encounter_power)
        
        if random.random() * 100 < success_chance:
            return {"outcome": "success"}
        else:
            return {"outcome": "failure"}
