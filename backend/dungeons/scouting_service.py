
from .models import PlayerDungeonState

class ScoutingService:

    COSTS = {
        1: 50,   # Initial Intel
        2: 150,  # Tactical Assessment
        3: 400   # Full Reconnaissance
    }

    @staticmethod
    def scout_dungeon(user, dungeon_id, stage):
        player_state, _ = PlayerDungeonState.objects.get_or_create(user=user)
        manifest = player_state.gate_manifest

        dungeon_data = next((d for d in manifest if d['dungeon_id'] == dungeon_id), None)

        if not dungeon_data:
            raise Exception("Dungeon not found in manifest.")

        # Prevent re-scouting at a stage the player already has.
        current_stage = dungeon_data.get('scouting_stage', 0)
        if stage <= current_stage:
            # If they are trying to view the same or a lower stage, just return the data without charging.
            return ScoutingService.get_scouted_data(dungeon_data)

        # Check if the user can afford the next stage.
        cost = ScoutingService.COSTS.get(stage, 0)
        if user.gamecoin < cost:
            raise Exception(f"Not enough GameCoin to scout. Cost: {cost}")

        # Deduct the cost and update the stage.
        user.gamecoin -= cost
        user.save()

        dungeon_data['scouting_stage'] = stage
        player_state.save()

        return ScoutingService.get_scouted_data(dungeon_data)

    @staticmethod
    def get_scouted_data(dungeon_data):
        scouted_data = {
            'name': dungeon_data['name'],
            'rank': dungeon_data['rank']
        }

        scouting_stage = dungeon_data.get('scouting_stage', 0)

        if scouting_stage >= 1:
            scouted_data['total_floors'] = dungeon_data['total_floors']
        
        if scouting_stage >= 2:
            scouted_data['monster_types'] = dungeon_data.get('monster_types', [])
            scouted_data['loot_category'] = dungeon_data.get('loot_category', [])

        if scouting_stage >= 3:
            final_boss_id = dungeon_data['encounter_log'][-1]['floor_guardian']['entity_id']
            # In a real implementation, you would fetch the boss's name from the database.
            scouted_data['final_boss'] = f"Entity #{final_boss_id}"
            scouted_data['rare_drops'] = dungeon_data.get('rare_drops', [])

        return scouted_data
