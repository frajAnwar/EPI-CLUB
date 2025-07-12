
from django.core.management.base import BaseCommand, CommandError
from accounts.models import User
from dungeons.dungeon_manifest_service import DungeonManifestService

class Command(BaseCommand):
    help = 'Regenerates the dungeon manifest for a specific user.'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='The ID of the user to regenerate the manifest for.')

    def handle(self, *args, **options):
        user_id = options['user_id']
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise CommandError(f'User with ID "{user_id}" does not exist.')

        self.stdout.write(f"Regenerating manifest for user: {user.email}")
        DungeonManifestService.generate_daily_manifest(user)
        self.stdout.write(self.style.SUCCESS(f'Successfully regenerated manifest for user: {user.email}'))
