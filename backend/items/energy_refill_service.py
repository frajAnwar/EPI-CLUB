from dungeons.models import PlayerEnergy
from items.models import Item
from accounts.models import Inventory
from transactions.models import InventoryTransaction

def use_item_for_energy(user, item_id):
    item = Item.objects.get(id=item_id)
    if not item.is_energy_refill:
        return {'detail': 'This item does not refill energy.'}
    try:
        player_energy = PlayerEnergy.objects.get(user=user)
    except PlayerEnergy.DoesNotExist:
        return {'detail': 'No energy record found.'}
    # Check if user has the item in inventory
    inv = Inventory.objects.filter(user=user, item=item).first()
    if not inv or inv.quantity < 1:
        return {'detail': 'You do not have this item.'}
    # Refill energy (up to max)
    before = player_energy.current_amount
    player_energy.current_amount = min(player_energy.current_amount + item.refill_amount, player_energy.max_amount)
    player_energy.save()
    # Remove one item from inventory
    inv.quantity -= 1
    inv.save()
    # Log the transaction
    InventoryTransaction.objects.create(
        user=user,
        item=item,
        quantity=-1,
        action="use",
        source="energy_refill",
        metadata={"refill_amount": item.refill_amount},
        before_quantity=before,
        after_quantity=player_energy.current_amount,
    )
    return {'detail': f'Energy refilled by {item.refill_amount}. Current energy: {player_energy.current_amount}'}
