class LevelingService:
    @staticmethod
    def calculate_xp_for_next_level(level):
        # Implements the formula: XP = 1000 * (level ^ 1.5)
        return int(1000 * (level ** 1.5))

    @staticmethod
    def grant_xp(user, xp_amount):
        user.xp += xp_amount
        xp_for_next_level = LevelingService.calculate_xp_for_next_level(user.level)

        while user.xp >= xp_for_next_level:
            user.level += 1
            user.xp -= xp_for_next_level
            # Grant level up rewards (e.g., talent points)
            # This could be handled by an event bus in a real application
            xp_for_next_level = LevelingService.calculate_xp_for_next_level(user.level)
        
        user.save()
