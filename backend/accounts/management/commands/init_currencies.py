from django.core.management.base import BaseCommand
from accounts.models import Currency

class Command(BaseCommand):
    help = 'Initialize the currencies in the database'

    def handle(self, *args, **options):
        Currency.objects.get_or_create(code='game', name='Game Coin')
        Currency.objects.get_or_create(code='club', name='Club Coin')
        self.stdout.write(self.style.SUCCESS('Currencies initialized successfully'))
