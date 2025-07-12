
import random
import json
import logging
from .models import Dungeon, WorldZone, WorldEvent, PlayerDungeonState, DungeonRun, Entity, TacticalApproach
from items.models import Item
from .talent_services import TalentService
from .encounter_services import EncounterService
from .loot_services import LootService
from .critical_event_services import CriticalEventService
from .floor_generation_service import FloorGenerationService
from accounts.leveling_service import LevelingService

from django.utils import timezone
from datetime import timedelta

# Constants
INITIAL_FLOOR_DURATION_MINUTES = 1
DEFAULT_FLOOR_DURATION_MINUTES = 1
BASE_PLAYER_POWER_MULTIPLIER = 18

class DungeonEngine:
    def __init__(self, user):
        self.user = user

    def start_expedition(self, dungeon_run_id):
        dungeon_run = DungeonRun.objects.get(id=dungeon_run_id, user=self.user)
        if dungeon_run.status != 'not_started':
            raise Exception("This dungeon run has already started.")

        # Generate the encounter log for the entire dungeon run
        encounter_log = []
        for i in range(dungeon_run.total_floors):
            floor_data = FloorGenerationService.generate_floor(
                dungeon_run.dungeon,
                dungeon_run.total_floors,
                i + 1
            )
            encounter_log.append(floor_data)
        
        dungeon_run.encounter_log = encounter_log
        dungeon_run.status = 'advancing'  # Start advancing on the first floor immediately
        dungeon_run.floor_completion_time = timezone.now() + timedelta(minutes=INITIAL_FLOOR_DURATION_MINUTES) # Set timer for the first floor
        dungeon_run.save()
        return self.get_run_state(dungeon_run.id)

    def advance_floor(self, dungeon_run_id, choice_id=None):
        dungeon_run = DungeonRun.objects.get(id=dungeon_run_id, user=self.user)

        if dungeon_run.status != 'in_progress':
            raise Exception("You must be in the Sanctuary to advance.")

        # 1. Apply effects from player's choice (if any)
        if choice_id:
            self._apply_player_choice(dungeon_run, choice_id)

        # 2. Set the timer for floor completion and update the run state
        dungeon_run.floor_completion_time = timezone.now() + timedelta(minutes=DEFAULT_FLOOR_DURATION_MINUTES)
        dungeon_run.current_encounter_index = 0
        dungeon_run.status = 'advancing'
        dungeon_run.save()

        return self.get_run_state(dungeon_run.id)

    def advance_encounter(self, dungeon_run_id):
        dungeon_run = DungeonRun.objects.get(id=dungeon_run_id, user=self.user)

        self._resolve_encounter(dungeon_run)
        
        # Only change status if the run hasn't already failed during resolution.
        if dungeon_run.status != 'failed':
            dungeon_run.status = 'encounter_resolved'
        
        # Always stop the timer after an encounter is resolved or failed.
        dungeon_run.floor_completion_time = None
        dungeon_run.save()

        return self.get_run_state(dungeon_run.id)

    def proceed_to_next_encounter(self, dungeon_run_id):
        dungeon_run = DungeonRun.objects.get(id=dungeon_run_id, user=self.user)
        if dungeon_run.status != 'encounter_resolved':
            raise Exception("You can only proceed after an encounter has been resolved.")

        # Grant rewards for the completed floor
        floor_log = dungeon_run.encounter_log[dungeon_run.current_floor - 1]
        floor_rewards = LootService.calculate_floor_rewards(floor_log)
        dungeon_run.unclaimed_rewards.append(floor_rewards)

        # Transition to the Sanctuary
        dungeon_run.current_floor += 1
        dungeon_run.current_encounter_index = 0
        if dungeon_run.current_floor > dungeon_run.total_floors:
            dungeon_run.status = 'completed'
        else:
            dungeon_run.status = 'in_progress'

        dungeon_run.save()
        return self.get_run_state(dungeon_run.id)

    def get_run_state(self, dungeon_run_id):
        dungeon_run = DungeonRun.objects.get(id=dungeon_run_id, user=self.user)
        player_power = self._get_player_power(dungeon_run)

        base_state = {
            "run_id": dungeon_run.id,
            "dungeon_name": dungeon_run.dungeon.name,
            "status": dungeon_run.status,
            "current_floor": dungeon_run.current_floor,
            "total_floors": dungeon_run.total_floors,
            "anima": dungeon_run.anima,
            "player_power": player_power,
        }

        if dungeon_run.status == 'advancing':
            floor_data = dungeon_run.encounter_log[dungeon_run.current_floor - 1]
            encounter_data = floor_data['encounters'][0]

            # --- Robustness Check for old data structures ---
            if 'total_power' not in encounter_data:
                raise Exception("This dungeon run is from an older version. Please abandon it and start a new one.")

            success_chance = EncounterService.calculate_success_chance(player_power, encounter_data['total_power'])

            base_state.update({
                "floor_completion_time": dungeon_run.floor_completion_time.isoformat(),
                "current_encounter": {
                    'entities': encounter_data['entities'],
                    'total_power': encounter_data['total_power'],
                    'success_chance': round(success_chance, 2)
                }
            })

        elif dungeon_run.status == 'encounter_resolved':
            base_state['last_encounter_result'] = dungeon_run.last_encounter_result

        elif dungeon_run.status == 'in_progress':
            # Now correctly points to the *next* floor's log
            next_floor_data = dungeon_run.encounter_log[dungeon_run.current_floor -1]
            base_state.update({
                "last_floor_results": dungeon_run.last_floor_results,
                "choices": {
                    "tactical_approaches": next_floor_data.get('tactical_approaches', []),
                    "critical_event": None # Placeholder
                }
            })

        elif dungeon_run.status in ['completed', 'failed']:
            base_state['rewards'] = dungeon_run.rewards
            base_state['unclaimed_rewards'] = dungeon_run.unclaimed_rewards

        return base_state

    def _resolve_encounter(self, dungeon_run):
        """
        Resolves a single encounter and updates the run state with the result.
        This method does NOT handle advancing the floor or encounter index.
        """
        floor_log = dungeon_run.encounter_log[dungeon_run.current_floor - 1]
        encounter_log_entry = floor_log['encounters'][0]

        if 'total_power' not in encounter_log_entry:
            raise Exception("This dungeon run is from an older version. Please abandon it and start a new one.")
        
        player_power = self._get_player_power(dungeon_run)
        encounter_power = encounter_log_entry['total_power']

        # --- Get enemy names first for use in all outcomes ---
        enemy_string = self._get_enemy_string(encounter_log_entry)

        result = EncounterService.resolve_encounter(player_power, encounter_power)
        
        encounter_result_data = {}
        if result['outcome'] == 'failure':
            summary_text = f"You were defeated by {enemy_string}."
            if dungeon_run.anima > 0:
                dungeon_run.anima -= 1
                summary_text += " You lost 1 Anima."

            if dungeon_run.anima <= 0:
                dungeon_run.status = 'failed'
                summary_text += " With no Anima left, your expedition has failed."

            encounter_result_data = {
                'outcome': 'failure',
                'enemy': enemy_string,
                'summary_text': summary_text
            }
        else: # Success
            total_loot = {'xp': 0, 'coins': 0, 'items': []}

            for entity_data in encounter_log_entry['entities']:
                entity = Entity.objects.get(id=entity_data['entity_id'])
                loot = LootService.generate_loot(entity)
                total_loot['xp'] += loot.get('xp', 0)
                total_loot['coins'] += loot.get('coins', 0)
                total_loot['items'].extend(loot.get('items', []))

            # The loot generated here is for the immediate encounter result display.
            # It is NOT added to the final unclaimed_rewards list here. That happens
            # when the floor is fully cleared in the proceed_to_next_encounter method.

            # Store the raw loot data in the encounter log for later aggregation.
            encounter_log_entry['result'] = {
                'outcome': 'success',
                'loot': total_loot
            }

            # Create a separate, enriched version of the loot for the immediate API response.
            loot_for_response = total_loot.copy()
            item_ids = [item['item_id'] for item in loot_for_response.get('items', [])]
            if item_ids:
                items = Item.objects.filter(id__in=item_ids).in_bulk()
                enriched_items = []
                for item_data in total_loot['items']:
                    item_id = item_data['item_id']
                    if item_id in items:
                        item_obj = items[item_id]
                        enriched_items.append({
                            'id': item_id,
                            'name': item_obj.name,
                            'quantity': item_data['quantity'],
                            'icon_url': item_obj.icon.url if item_obj.icon else 'https://via.placeholder.com/40'
                        })
                loot_for_response['items'] = enriched_items

            encounter_result_data = {
                'outcome': 'success',
                'enemy': enemy_string,
                'summary_text': f"You defeated the enemy squad and found some loot!",
                'loot': loot_for_response
            }
        
        # The last_encounter_result is for the immediate API response, so it should be enriched.
        dungeon_run.last_encounter_result = encounter_result_data

        # If this was the last encounter, calculate and store the floor summary
        is_last_encounter = dungeon_run.current_encounter_index >= len(floor_log['encounters']) - 1
        if is_last_encounter:
            # Clear modifiers for the next floor
            dungeon_run.active_modifiers = []

    
    def _apply_player_choice(self, dungeon_run, choice_id):
        try:
            approach = TacticalApproach.objects.get(id=choice_id)
            
            if not approach.effects:
                return

            raw_effects = approach.effects
            
            # Defensively parse if it's a string
            if isinstance(raw_effects, str):
                try:
                    effects_data = json.loads(raw_effects)
                except json.JSONDecodeError:
                    logging.error(f"Could not decode effects for approach {choice_id}")
                    return
            else:
                effects_data = raw_effects

            # The data should be a dictionary with an 'effects' key containing a list
            if isinstance(effects_data, dict):
                effects_list = effects_data.get('effects', [])
                if effects_list:
                    # We extend the list with the new effects, not append the whole block
                    dungeon_run.active_modifiers.extend(effects_list)

            # Log the choice for record-keeping
            dungeon_run.tactical_approach_log.append({
                'choice_id': choice_id,
                'name': approach.name,
                'effects_applied': effects_data
            })

            dungeon_run.save()

        except TacticalApproach.DoesNotExist:
            logging.warning(f"Could not find TacticalApproach with id: {choice_id}")
            pass

    def _get_enemy_string(self, encounter_log_entry):
        squad_names = [entity_data['name'] for entity_data in encounter_log_entry['entities']]
        if not squad_names:
            return "an unknown enemy"

        squad_counts = {}
        for name in squad_names:
            squad_counts[name] = squad_counts.get(name, 0) + 1
        
        enemy_string_parts = []
        for name, count in squad_counts.items():
            if count > 1:
                enemy_string_parts.append(f"{count} x {name}")
            else:
                enemy_string_parts.append(name)
        return ", ".join(enemy_string_parts)

    def _get_player_power(self, dungeon_run):
        base_power = self.user.level * BASE_PLAYER_POWER_MULTIPLIER
        player_stats = {'power': base_power}

        # active_modifiers is now a flat list of effect dictionaries
        for effect in dungeon_run.active_modifiers:
            if isinstance(effect, dict) and effect.get('type') == 'PLAYER_MODIFIER' and effect.get('stat') == 'PlayerPower':
                operation = effect.get('operation')
                value = effect.get('value')
                if operation == 'ADD':
                    player_stats['power'] += value
                elif operation == 'MULTIPLY':
                    player_stats['power'] *= value

        # Placeholder for talent effects
        # player_stats = TalentService.apply_talent_effects(self.user, player_stats)
        return player_stats['power']

    def abandon_expedition(self, dungeon_run_id):
        dungeon_run = DungeonRun.objects.get(id=dungeon_run_id, user=self.user)
        if dungeon_run.status not in ['in_progress', 'advancing', 'encounter_resolved', 'floor_completed']:
            raise Exception("This dungeon run cannot be abandoned in its current state.")

        dungeon_run.status = 'abandoned'
        dungeon_run.end_time = timezone.now()
        dungeon_run.save()

        return {"message": "Expedition abandoned successfully."}
