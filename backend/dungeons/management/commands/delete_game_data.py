from django.core.management.base import BaseCommand
from dungeons.models import Dungeon, Entity
from items.models import Item

class Command(BaseCommand):
    help = 'Deletes all Dungeon, Entity, and Item data from the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('This will delete all Dungeon, Entity, and Item data.'))
        confirmation = input('Are you sure you want to continue? (yes/no): ')

        if confirmation.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Operation cancelled.'))
            return

        dungeon_count, _ = Dungeon.objects.all().delete()
        entity_count, _ = Entity.objects.all().delete()
        item_count, _ = Item.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {dungeon_count} dungeons, {entity_count} entities, and {item_count} items.'))
