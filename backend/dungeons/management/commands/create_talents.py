from django.core.management.base import BaseCommand
from dungeons.models import Talent

class Command(BaseCommand):
    help = 'Creates the initial talents for the Constellation of the Hunter'

    def handle(self, *args, **options):
        self.stdout.write('Creating talents...')

        # The Eye of the Observer
        Talent.objects.create(
            name='Efficient Probing',
            description='Reduces GameCoin cost of scouting by 3% per rank.',
            tree='The Eye of the Observer',
            max_rank=5,
            rank_bonuses=[{'stat': 'scout_cost_redux', 'value': 0.03}],
            required_rank='E'
        )
        Talent.objects.create(
            name='Rapid Analysis',
            description='Reduces expedition floor timers by 2% per rank.',
            tree='The Eye of the Observer',
            max_rank=3,
            rank_bonuses=[{'stat': 'expedition_timer_redux', 'value': 0.02}],
            required_rank='D'
        )

        # The Hand of Fortune
        Talent.objects.create(
            name='Treasure Hunter',
            description='Increases GameCoin found in dungeons by 2% per rank.',
            tree='The Hand of Fortune',
            max_rank=5,
            rank_bonuses=[{'stat': 'dungeon_coin_bonus', 'value': 0.02}],
            required_rank='E'
        )
        Talent.objects.create(
            name='Resourceful Scavenger',
            description='1% chance per rank for double crafting material drops.',
            tree='The Hand of Fortune',
            max_rank=5,
            rank_bonuses=[{'stat': 'double_craft_chance', 'value': 0.01}],
            required_rank='D'
        )

        # The Path of the Dominator
        Talent.objects.create(
            name='Overwhelm',
            description='+1% expedition success chance per rank for each rank the gate is below your own.',
            tree='The Path of the Dominator',
            max_rank=5,
            rank_bonuses=[{'stat': 'overwhelm_bonus', 'value': 0.01}],
            required_rank='E'
        )
        Talent.objects.create(
            name='Tenacity',
            description='Reduces the duration of any failed \"System Mandate\" penalty by 1 hour per rank.',
            tree='The Path of the Dominator',
            max_rank=3,
            rank_bonuses=[{'stat': 'penalty_duration_redux', 'value': 3600}],
            required_rank='D'
        )

        self.stdout.write(self.style.SUCCESS('Successfully created talents.'))
