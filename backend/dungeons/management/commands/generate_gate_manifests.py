import random
from django.core.management.base import BaseCommand
from accounts.models import User
from dungeons.models import Dungeon, DungeonRun, PlayerDungeonState
from dungeons.encounter_services import EncounterService

class Command(BaseCommand):
    help = "Generate daily Gate Manifest and associated DungeonRun objects for each player."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- Starting Gate Manifest Generation ---"))
        
        for user in User.objects.filter(is_active=True):
            manifest = self._generate_manifest_for_user(user)
            state, _ = PlayerDungeonState.objects.get_or_create(user=user)
            state.gate_manifest = manifest
            state.save()
            self.stdout.write(f"Generated {len(manifest)} gates for {user.email} (Rank: {getattr(user, 'rank', 'E')}).")

        self.stdout.write(self.style.SUCCESS("--- Gate Manifest Generation Complete ---"))

    def _generate_manifest_for_user(self, user):
        player_rank = getattr(user, 'rank', 'E')
        ranks = ['E', 'D', 'C', 'B', 'A', 'S', 'SS', 'SSS', 'National']
        player_rank_index = ranks.index(player_rank) if player_rank in ranks else 0

        choices = [player_rank]
        weights = [0.7]
        if player_rank_index + 1 < len(ranks):
            choices.append(ranks[player_rank_index + 1])
            weights.append(0.2)
        if player_rank_index > 0:
            choices.append(ranks[player_rank_index - 1])
            weights.append(0.1)

        num_gates = random.randint(3, 5)
        manifest = []
        for _ in range(num_gates):
            assigned_rank = random.choices(choices, weights=weights, k=1)[0]
            dungeon = self._get_dungeon_for_rank(assigned_rank)

            if dungeon:
                run = DungeonRun.objects.create(
                    user=user,
                    dungeon=dungeon,
                    total_floors=random.randint(3, 5),
                    status='not_started'
                )
                run.encounter_log = EncounterService.generate_floor_plan(run)
                run.save()
                manifest.append({
                    "run_id": run.id,
                    "dungeon_name": dungeon.name,
                    "dungeon_rank": dungeon.rank,
                })
        return manifest

    def _get_dungeon_for_rank(self, rank):
        dungeons = Dungeon.objects.filter(rank=rank, is_active=True, zone__isnull=False)
        if dungeons.exists():
            return random.choice(list(dungeons))
        
        # Fallback to other ranks if no dungeon is found
        ranks = ['E', 'D', 'C', 'B', 'A', 'S', 'SS', 'SSS', 'National']
        rank_index = ranks.index(rank) if rank in ranks else 0
        search_indices = []
        i = 1
        while len(search_indices) < len(ranks) - 1:
            if rank_index - i >= 0:
                search_indices.append(rank_index - i)
            if rank_index + i < len(ranks):
                search_indices.append(rank_index + i)
            i += 1

        for i in search_indices:
            fallback_rank = ranks[i]
            dungeons = Dungeon.objects.filter(rank=fallback_rank, is_active=True, zone__isnull=False)
            if dungeons.exists():
                return random.choice(list(dungeons))
        return None
