
from celery import shared_task
from .dungeon_manifest_service import DungeonManifestService
from accounts.models import User

@shared_task
def generate_daily_manifests_for_all_users():
    """A daily task to generate a new gate manifest for every user."""
    print("--- Running Daily Manifest Generation Task ---")
    users = User.objects.filter(is_active=True)
    for user in users:
        print(f"Generating manifest for {user.email}...")
        DungeonManifestService.generate_daily_manifest(user)
    print("--- Daily Manifest Generation Complete ---")
