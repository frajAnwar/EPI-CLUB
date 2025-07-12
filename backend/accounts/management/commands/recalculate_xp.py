
from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Recalculates the next_level_xp for all users based on the new formula.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting XP recalculation for all users...'))
        
        for user in User.objects.all():
            user.next_level_xp = int(250 * (user.level ** 1.35))
            user.save()

        self.stdout.write(self.style.SUCCESS('Successfully recalculated next_level_xp for all users.'))
