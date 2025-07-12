
import random
from .models import WorldZone, PlayerGate, Dungeon

class MapDataService:
    @staticmethod
    def get_map_data(user):
        zones = WorldZone.objects.all()
        player_gates = PlayerGate.objects.filter(user=user).select_related('dungeon__zone')

        if not player_gates.exists():
            from .dungeon_manifest_service import DungeonManifestService
            DungeonManifestService.generate_daily_manifest(user)
            player_gates = PlayerGate.objects.filter(user=user).select_related('dungeon__zone')

        zones_data = []
        for zone in zones:
            dungeons_in_zone = []
            for gate in player_gates:
                if gate.dungeon.zone == zone:
                    dungeons_in_zone.append({
                        'id': gate.id,
                        'name': gate.dungeon.name,
                        'rank': gate.dungeon.rank,
                        'map_x': gate.map_x,
                        'map_y': gate.map_y,
                        'is_completed': gate.is_completed,
                        'is_lost': gate.is_lost,
                    })
            
            zones_data.append({
                'id': zone.id,
                'name': zone.name,
                'world_map_x': zone.world_map_x,
                'world_map_y': zone.world_map_y,
                'dungeons': dungeons_in_zone,
            })
        
        return zones_data
