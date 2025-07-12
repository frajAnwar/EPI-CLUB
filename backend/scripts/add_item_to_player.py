
import os
import django
import sys
import argparse

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_rpg.settings')
django.setup()

from django.contrib.auth import get_user_model
from items.models import Item
from transactions.services import atomic_item_currency_transfer

def main():
    parser = argparse.ArgumentParser(description='Adds a specified quantity of an item to a user\'s inventory.')
    parser.add_argument('username', type=str, help='The username of the user to receive the item.')
    parser.add_argument('item_id', type=int, help='The ID of the item to add.')
    parser.add_argument('quantity', type=int, help='The quantity of the item to add.')

    args = parser.parse_args()

    User = get_user_model()
    try:
        user = User.objects.get(username=args.username)
    except User.DoesNotExist:
        print(f'Error: User with username "{args.username}" does not exist.')
        return

    try:
        item = Item.objects.get(id=args.item_id)
    except Item.DoesNotExist:
        print(f'Error: Item with ID "{args.item_id}" does not exist.')
        return

    try:
        atomic_item_currency_transfer(
            user=user,
            item=item,
            item_delta=args.quantity,
            currency=None,
            currency_delta=0,
            action='ADMIN_GRANT',
            source='Management Script'
        )
        print(f'Successfully added {args.quantity} of "{item.name}" to {user.username}.')
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == '__main__':
    main()
