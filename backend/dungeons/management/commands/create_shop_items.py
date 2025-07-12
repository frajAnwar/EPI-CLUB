from django.core.management.base import BaseCommand
from dungeons.models import ShopItem
from items.models import Item

class Command(BaseCommand):
    help = 'Creates the initial shop items'

    def handle(self, *args, **options):
        self.stdout.write('Creating shop items...')

        # Hunter Supplies
        mana_probe = Item.objects.create(name='Mana Probe', description='A basic probe to measure mana levels.')
        ShopItem.objects.create(
            item=mana_probe,
            cost_game_coin=100,
            is_hunter_supply=True
        )

        sturdy_compass = Item.objects.create(name='Sturdy Compass', description='A reliable compass for expeditions.')
        ShopItem.objects.create(
            item=sturdy_compass,
            cost_game_coin=250,
            is_hunter_supply=True
        )

        # Club Store
        containment_unit = Item.objects.create(name='Containment Unit', description='A device to contain unstable gate fragments.')
        ShopItem.objects.create(
            item=containment_unit,
            cost_club_coin=50,
            is_club_store=True
        )

        self.stdout.write(self.style.SUCCESS('Successfully created shop items.'))
