
from .models import User

class LevelingService:
    @staticmethod
    def add_xp(user, amount):
        user.xp += amount
        while user.xp >= user.next_level_xp:
            user.xp -= user.next_level_xp
            LevelingService.level_up(user)
        user.save()

    @staticmethod
    def level_up(user):
        user.level += 1
        user.talent_points += 1
        # Adjusted the formula for a smoother curve
        user.next_level_xp = int(250 * (user.level ** 1.35))
        LevelingService.update_rank(user)
        user.save()

    @staticmethod
    def update_rank(user):
        if user.level >= 100:
            user.rank = 'National'
        elif user.level >= 90:
            user.rank = 'SSS'
        elif user.level >= 70:
            user.rank = 'SS'
        elif user.level >= 60:
            user.rank = 'S'
        elif user.level >= 40:
            user.rank = 'A'
        elif user.level >= 20:
            user.rank = 'B'
        elif user.level >= 8:
            user.rank = 'C'
        elif user.level >= 4:
            user.rank = 'D'
        else:
            user.rank = 'E'
