from django.core.management.base import BaseCommand
from django.utils import timezone
from dungeons.models import Dungeon, WorldZone, PlayerDungeonState
import random

ANOMALY_TYPES = ["Swarm", "Elite", "Volatile"]
DUNGEON_BREAK_DAYS = 7

class Command(BaseCommand):
    help = "Update dungeon instability, trigger/reset anomalies, and handle Dungeon Breaks."

    def handle(self, *args, **options):
        now = timezone.now()
        for dungeon in Dungeon.objects.all():
            # If anomaly is active and expired, reset anomaly
            if dungeon.anomaly_state and dungeon.anomaly_active_until and now >= dungeon.anomaly_active_until:
                dungeon.anomaly_state = ""
                dungeon.instability_level = 0
                dungeon.anomaly_active_until = None
                self.stdout.write(f"Reset anomaly for {dungeon.name}")
                dungeon.save()
                continue

            # If anomaly is not active, increment instability
            if not dungeon.anomaly_state:
                # Increment instability for dungeons not cleared recently
                last_cleared = None
                player_states = PlayerDungeonState.objects.filter(dungeon=dungeon)
                if player_states.exists():
                    last_cleared = max([ps.last_completed for ps in player_states if ps.last_completed], default=None)
                if not last_cleared or (now - last_cleared).days >= 1:
                    dungeon.instability_level = min(100, dungeon.instability_level + 10)
                if dungeon.instability_level >= 100:
                    # Trigger anomaly
                    dungeon.anomaly_state = random.choice(ANOMALY_TYPES)
                    dungeon.anomaly_active_until = now + timezone.timedelta(hours=24)
                    self.stdout.write(f"Triggered anomaly {dungeon.anomaly_state} for {dungeon.name}")
                dungeon.save()

            # Dungeon Break: if ignored for DUNGEON_BREAK_DAYS
            last_found = None
            player_states = PlayerDungeonState.objects.filter(dungeon=dungeon)
            if player_states.exists():
                last_found = max([ps.last_found for ps in player_states if ps.last_found], default=None)
            if last_found and (now - last_found).days >= DUNGEON_BREAK_DAYS:
                # Mark the associated WorldZone as Infestation Zone
                if hasattr(dungeon, 'zone') and dungeon.zone:
                    zone = dungeon.zone
                    zone.is_saturated = True  # Reuse is_saturated for Infestation for now
                    zone.saturation_expires_at = now + timezone.timedelta(days=1)
                    zone.save()
                    self.stdout.write(f"Dungeon Break! {dungeon.name} caused Infestation in {zone.name}")
                # Placeholder: set a community progress bar (could be a field on WorldZone)
                # Placeholder: send notifications to players (not implemented here)
