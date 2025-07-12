
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from dungeons.models import PlayerGate

class Command(BaseCommand):
    help = "Fetches and displays the map coordinates for a specific user\'s gates."

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help="The ID of the user to inspect.")

    def handle(self, *args, **options):
        User = get_user_model()
        user_id = options['user_id']

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with ID {user_id} not found."))
            return

        gates = PlayerGate.objects.filter(user=user)

        if not gates.exists():
            self.stdout.write(self.style.WARNING(f"No gates found for user: {user.username}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Gate coordinates for user: {user.username} (ID: {user_id})"))
        for gate in gates:
            self.stdout.write(f"  - {gate.dungeon.name}: (x: {gate.map_x}, y: {gate.map_y})")
