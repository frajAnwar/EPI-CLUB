
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import random
from .engine import DungeonEngine
from .models import Dungeon, DungeonRun, WorldZone, ActiveWorldEvent, PlayerDungeonState, PlayerGate
from .dungeon_manifest_service import DungeonManifestService

# --- Placeholder Views ---
class HunterDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({"message": "Hunter Dashboard"})

from .scouting_service import ScoutingService

class DungeonScoutingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        dungeon_id = kwargs.get('dungeon_id')
        stage = request.data.get('stage')

        if not dungeon_id or not stage:
            return Response({"error": "Dungeon ID and stage are required."}, status=400)

        try:
            scouted_data = ScoutingService.scout_dungeon(request.user, dungeon_id, stage)
            return Response(scouted_data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class DungeonRunView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({"message": "Dungeon Run"})

class DungeonBreakActiveView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Dungeon Break Active"})

class DungeonBreakParticipateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        return Response({"message": "Dungeon Break Participate"})

class RedGateDetailView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Red Gate Detail"})

class UserProvisionsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({"message": "User Provisions"})

class GenerateGatesView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Generate Gates"})

class CreateStarterDungeonView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Create Starter Dungeon"})

class RunMigrationsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Run Migrations"})

class ActiveEventsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Active Events"})

class EventTriggerView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({"message": "Event Trigger"})

class TalentTreeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({"message": "Talent Tree"})

class SpendTalentPointView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        return Response({"message": "Spend Talent Point"})

class ShopView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Shop"})

class PurchaseItemView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        return Response({"message": "Purchase Item"})

class MarketplaceView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Marketplace"})

class PurchaseListingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        return Response({"message": "Purchase Listing"})


from .map_data_service import MapDataService

class WorldZonesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        zones_data = MapDataService.get_map_data(request.user)
        active_run = DungeonRun.objects.filter(user=request.user, status__in=['in_progress', 'advancing']).first()
        active_run_data = {
            'id': active_run.id,
            'dungeon_id': active_run.dungeon.id
        } if active_run else None

        return Response({
            'zones': zones_data,
            'active_run': active_run_data,
        })

from accounts.leveling_service import LevelingService
from .loot_services import LootService
from items.models import Item
from django.db import transaction
from transactions.services import atomic_item_currency_transfer

class ClaimRewardsView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        dungeon_run_id = request.data.get('dungeon_run_id')
        if not dungeon_run_id:
            return Response({"error": "Dungeon Run ID is required."}, status=400)

        try:
            dungeon_run = DungeonRun.objects.get(id=dungeon_run_id, user=request.user)
            if not dungeon_run.unclaimed_rewards:
                return Response({"message": "No rewards to claim."})

            total_xp = 0
            total_coins = 0
            items_granted = []

            for reward_group in dungeon_run.unclaimed_rewards:
                total_xp += reward_group.get('xp', 0)
                total_coins += reward_group.get('coins', 0)
                for item_data in reward_group.get('items', []):
                    try:
                        # --- Compatibility for old and new data formats ---
                        item_id = item_data.get('item_id') or item_data.get('id')
                        if not item_id:
                            continue

                        quantity = item_data.get('quantity', 1)
                        item_to_add = Item.objects.get(id=item_id)
                        atomic_item_currency_transfer(
                            user=request.user,
                            item=item_to_add,
                            item_delta=quantity,
                            currency='GAME_COIN',
                            currency_delta=0,
                            action='DUNGEON_REWARD',
                            source=f"Dungeon Run: {dungeon_run.id}",
                            metadata={'dungeon_run_id': dungeon_run.id}
                        )
                        items_granted.append(item_to_add.name)
                    except Item.DoesNotExist:
                        failed_item_id = item_data.get('item_id') or item_data.get('id', 'N/A')
                        print(f"Could not find item with ID {failed_item_id} to grant as a reward.")
                    except (KeyError, TypeError):
                        print(f"Malformed item data in reward group: {item_data}")

            LevelingService.add_xp(request.user, total_xp)
            atomic_item_currency_transfer(
                user=request.user,
                item=None,
                item_delta=0,
                currency='GAME_COIN',
                currency_delta=total_coins,
                action='DUNGEON_REWARD',
                source=f"Dungeon Run: {dungeon_run.id}",
                metadata={'dungeon_run_id': dungeon_run.id}
            )

            dungeon_run.unclaimed_rewards = []
            dungeon_run.save()

            # Mark the gate as completed
            player_gate = PlayerGate.objects.get(user=request.user, dungeon=dungeon_run.dungeon)
            player_gate.is_completed = True
            player_gate.save()

            return Response({
                "message": "Rewards claimed successfully!",
                "xp_gained": total_xp,
                "coins_gained": total_coins,
                "items_granted": items_granted
            })
        except DungeonRun.DoesNotExist:
            return Response({"error": "Dungeon run not found."}, status=404)


# --- Interactive Expedition Views ---
class StartExpeditionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        gate_id = request.data.get('gate_id')
        if not gate_id:
            return Response({"error": "Gate ID is required."}, status=400)

        try:
            player_gate = PlayerGate.objects.get(user=request.user, id=gate_id)
        except PlayerGate.DoesNotExist:
            return Response({"error": "Gate not found for this player."}, status=404)

        if player_gate.is_completed:
            return Response({"error": "You have already completed this gate today."}, status=400)
        if player_gate.is_lost:
            return Response({"error": "This gate has been lost and cannot be re-entered today."}, status=400)

        active_run = DungeonRun.objects.filter(user=request.user, status__in=['in_progress', 'advancing']).first()
        if active_run:
            return Response({'run_id': active_run.id, 'message': 'Active run already in progress.'}, status=200)

        dungeon_run = DungeonRun.objects.create(
            user=request.user,
            dungeon=player_gate.dungeon,
            total_floors=player_gate.total_floors,
            encounter_log=player_gate.encounter_log
        )

        engine = DungeonEngine(request.user)
        run_state = engine.start_expedition(dungeon_run.id)

        return Response(run_state)

class DungeonRunStateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, run_id, *args, **kwargs):
        engine = DungeonEngine(request.user)
        try:
            run_state = engine.get_run_state(run_id)
            return Response(run_state)
        except DungeonRun.DoesNotExist:
            return Response({"error": "Dungeon run not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class AdvanceFloorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        dungeon_run_id = request.data.get('dungeon_run_id')
        choice_id = request.data.get('choice_id') # Can be from a tactical approach or a critical event

        if not dungeon_run_id:
            return Response({"error": "Dungeon Run ID is required."}, status=400)

        engine = DungeonEngine(request.user)
        try:
            run_state = engine.advance_floor(dungeon_run_id, choice_id)
            return Response(run_state)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class AdvanceEncounterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        dungeon_run_id = request.data.get('dungeon_run_id')
        if not dungeon_run_id:
            return Response({"error": "Dungeon Run ID is required."}, status=400)

        engine = DungeonEngine(request.user)
        try:
            run_state = engine.advance_encounter(dungeon_run_id)
            return Response(run_state)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class ProceedToNextEncounterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        dungeon_run_id = request.data.get('dungeon_run_id')
        if not dungeon_run_id:
            return Response({"error": "Dungeon Run ID is required."}, status=400)

        engine = DungeonEngine(request.user)
        try:
            run_state = engine.proceed_to_next_encounter(dungeon_run_id)
            return Response(run_state)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class AbandonExpeditionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        dungeon_run_id = request.data.get('dungeon_run_id')
        if not dungeon_run_id:
            return Response({"error": "Dungeon Run ID is required."}, status=400)

        engine = DungeonEngine(request.user)
        try:
            result = engine.abandon_expedition(dungeon_run_id)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

