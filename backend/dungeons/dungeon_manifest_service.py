
import random
from .models import Dungeon, PlayerDungeonState, WorldZone, PlayerGate
from accounts.models import User
from .floor_generation_service import FloorGenerationService

class DungeonManifestService:

    MIN_GATES_PER_ZONE = 3
    MAX_GATES_PER_ZONE = 5
    MIN_FLOORS = 4
    MAX_FLOORS = 8
    MAX_COORDINATE_OFFSET = 200

    @staticmethod
    def generate_daily_manifest(user: User):
        """
        Generates a daily manifest of dungeons for a given user.
        """
        PlayerGate.objects.filter(user=user).delete()

        for zone in WorldZone.objects.all():
            if not zone.rank_pool:
                continue

            possible_dungeons = list(Dungeon.objects.filter(zone=zone, rank__in=zone.rank_pool))
            if not possible_dungeons:
                continue

            num_to_spawn = random.randint(DungeonManifestService.MIN_GATES_PER_ZONE, min(DungeonManifestService.MAX_GATES_PER_ZONE, len(possible_dungeons)))
            selected_dungeons = random.sample(possible_dungeons, num_to_spawn)

            for dungeon in selected_dungeons:
                total_floors = random.randint(DungeonManifestService.MIN_FLOORS, DungeonManifestService.MAX_FLOORS)
                encounter_log = [FloorGenerationService.generate_floor(dungeon, total_floors, i + 1) for i in range(total_floors)]
                
                x_offset = random.randint(-DungeonManifestService.MAX_COORDINATE_OFFSET, DungeonManifestService.MAX_COORDINATE_OFFSET)
                y_offset = random.randint(-DungeonManifestService.MAX_COORDINATE_OFFSET, DungeonManifestService.MAX_COORDINATE_OFFSET)

                PlayerGate.objects.create(
                    user=user,
                    dungeon=dungeon,
                    map_x=zone.world_map_x + x_offset,
                    map_y=zone.world_map_y + y_offset,
                    total_floors=total_floors,
                    encounter_log=encounter_log,
                )
