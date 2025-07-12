import random

class ExpeditionFightingService:
    BASE_CHANCE = 0.50
    POWER_MODIFIER = 0.025

    def __init__(self, user, dungeon_run):
        self.user = user
        self.dungeon_run = dungeon_run

    def calculate_success_chance(self, floor_power):
        player_power = self.get_player_power()
        power_difference = player_power - floor_power
        
        talent_bonuses = self.get_talent_bonuses()
        difficulty_penalty = self.get_difficulty_penalty()

        success_chance = self.BASE_CHANCE + (power_difference * self.POWER_MODIFIER) + talent_bonuses - difficulty_penalty
        return max(0, min(1, success_chance)) # Clamp between 0 and 1

    def get_player_power(self):
        # Placeholder: Replace with actual calculation from user level and items
        return self.user.level * 10 # Example calculation

    def get_talent_bonuses(self):
        # Placeholder: Replace with actual calculation from user talents
        return 0.05 # Example bonus

    def get_difficulty_penalty(self):
        # Placeholder: Replace with actual calculation from dungeon state
        if self.dungeon_run.dungeon.anomaly_state == 'Anomaly':
            return 0.10
        elif self.dungeon_run.dungeon.anomaly_state == 'Red Gate':
            return 0.20
        return 0

    def fight_floor(self):
        floor_power = self.dungeon_run.dungeon.floor_power_levels[self.dungeon_run.current_floor - 1]
        success_chance = self.calculate_success_chance(floor_power)
        
        if random.random() < success_chance:
            return True, "You have successfully cleared the floor!"
        else:
            return False, "You have been defeated."
