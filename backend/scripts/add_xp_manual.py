
from accounts.models import User
from accounts.leveling_service import LevelingService

def run():
    try:
        user = User.objects.get(email='frajanwer9@gmail.com')
        print(f"User {user.email} found. Current XP: {user.xp}, Level: {user.level}")
        xp_to_add = 10000
        print(f"Adding {xp_to_add} XP...")
        LevelingService.add_xp(user, xp_to_add)
        user.refresh_from_db()
        print(f"XP added successfully. New XP: {user.xp}, New Level: {user.level}, New Rank: {user.rank}")
    except User.DoesNotExist:
        print("User with email frajanwer9@gmail.com not found.")

if __name__ == '__main__':
    run()
