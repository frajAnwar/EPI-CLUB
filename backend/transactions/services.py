from django.db import transaction
from .models import InventoryTransaction, CurrencyTransaction
from accounts.models import User, UserCurrency
from items.models import Item, InventoryItem


def atomic_item_currency_transfer(user, item, item_delta, currency, currency_delta, action, source, metadata=None):
    """
    Atomically update inventory and/or currency, and log all transactions.
    This function is safe to call with only an item, only currency, or both.
    """
    if metadata is None:
        metadata = {}
    
    inv_tx = None
    cur_tx = None

    with transaction.atomic():
        # --- Handle Item Transfer ---
        if item and item_delta != 0:
            GLOBAL_INVENTORY_LIMIT = 200
            PER_ITEM_LIMIT = getattr(item, 'max_per_user', 99)
            total_items = sum(i.quantity for i in InventoryItem.objects.filter(user=user))
            unique_id = metadata.get('unique_id')

            if unique_id:
                inv = InventoryItem.objects.create(user=user, item=item, quantity=1, unique_id=unique_id, metadata=metadata)
                before_qty = 0
                new_item_qty = 1
                if (total_items + 1) > GLOBAL_INVENTORY_LIMIT:
                    raise ValueError(f"Cannot hold more than {GLOBAL_INVENTORY_LIMIT} total items.")
            else:
                inv, _ = InventoryItem.objects.get_or_create(user=user, item=item, defaults={"quantity": 0})
                before_qty = inv.quantity
                new_item_qty = inv.quantity + item_delta
                if item_delta > 0:
                    if new_item_qty > PER_ITEM_LIMIT:
                        raise ValueError(f"Cannot hold more than {PER_ITEM_LIMIT} of this item.")
                    if (total_items + item_delta) > GLOBAL_INVENTORY_LIMIT:
                        raise ValueError(f"Cannot hold more than {GLOBAL_INVENTORY_LIMIT} total items.")
                inv.quantity = new_item_qty
                inv.save()
            
            inv_tx = InventoryTransaction.objects.create(
                user=user, item=item, quantity=item_delta, action=action, source=source,
                metadata=metadata, before_quantity=before_qty, after_quantity=new_item_qty
            )

        # --- Handle Currency Transfer ---
        if currency and currency_delta != 0:
            from accounts.models import Currency
            currency_obj = Currency.objects.get(code=currency)
            uc, _ = UserCurrency.objects.get_or_create(user=user, currency=currency_obj, defaults={"balance": 0})
            before_bal = uc.balance
            uc.balance += currency_delta
            uc.save()
            
            cur_tx = CurrencyTransaction.objects.create(
                user=user, currency=currency_obj, amount=currency_delta, action=action, source=source,
                metadata=metadata, before_balance=before_bal, after_balance=uc.balance
            )

    return inv_tx, cur_tx
