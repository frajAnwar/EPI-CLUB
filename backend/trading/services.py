from django.db import transaction
from accounts.models import Inventory, UserCurrency
from .models import ShopItem, Trade
from transactions.services import atomic_item_currency_transfer
from decimal import Decimal


def purchase_item(user, shop_item: ShopItem, quantity: int):
    """
    Atomically purchase an item from the shop, updating both Inventory and ShopItem stock,
    deducting user currency, and logging all transactions.
    Raises ValueError if not enough stock or insufficient funds.
    """
    if shop_item.stock < quantity:
        raise ValueError("Not enough stock in shop.")
    total_price = shop_item.price * Decimal(quantity)
    # Check user currency balance
    user_currency = UserCurrency.objects.filter(user=user, currency=shop_item.currency).first()
    if not user_currency or user_currency.balance < total_price:
        raise ValueError("Insufficient funds.")
    with transaction.atomic():
        # Update shop stock
        shop_item.stock -= quantity
        shop_item.save()
        # Atomic inventory/currency update and transaction log
        inv_tx, cur_tx = atomic_item_currency_transfer(
            user=user,
            item=shop_item.item,
            item_delta=quantity,
            currency=shop_item.currency,
            currency_delta=-total_price,
            action="purchase",
            source="shop",
            metadata={"shop_item_id": shop_item.id, "quantity": quantity}
        )
    return inv_tx


def atomic_trade(trade: Trade):
    """
    Atomically complete a player-to-player trade:
    - Transfers item from seller (from_user) to buyer (to_user)
    - Transfers currency from buyer to seller (minus fee)
    - Logs all transactions
    - Updates trade status to 'completed'
    """
    if trade.from_user == trade.to_user:
        raise ValueError("Cannot trade with yourself.")
    if trade.status != 'approved':
        raise ValueError("Trade must be approved before completion.")
    if trade.quantity <= 0:
        raise ValueError("Invalid trade quantity.")
    total_price = trade.price
    fee = trade.fee or Decimal('0')
    net_to_seller = total_price - fee
    with transaction.atomic():
        # Check seller inventory
        seller_inv = Inventory.objects.filter(user=trade.from_user, item=trade.item).first()
        if not seller_inv or seller_inv.quantity < trade.quantity:
            raise ValueError("Seller does not have enough items.")
        # Check buyer currency
        buyer_currency = UserCurrency.objects.filter(user=trade.to_user, currency=trade.currency).first()
        if not buyer_currency or buyer_currency.balance < total_price:
            raise ValueError("Buyer does not have enough currency.")
        # Transfer item from seller to buyer
        seller_inv.quantity -= trade.quantity
        seller_inv.save()
        buyer_inv, _ = Inventory.objects.get_or_create(user=trade.to_user, item=trade.item, defaults={"quantity": 0})
        before_qty = buyer_inv.quantity
        buyer_inv.quantity += trade.quantity
        buyer_inv.save()
        # Log inventory transactions
        from transactions.models import InventoryTransaction, CurrencyTransaction
        InventoryTransaction.objects.create(
            user=trade.from_user,
            item=trade.item,
            quantity=-trade.quantity,
            action="trade",
            source="trade",
            metadata={"trade_id": trade.id, "to_user": trade.to_user.id},
            before_quantity=seller_inv.quantity + trade.quantity,
            after_quantity=seller_inv.quantity,
        )
        InventoryTransaction.objects.create(
            user=trade.to_user,
            item=trade.item,
            quantity=trade.quantity,
            action="trade",
            source="trade",
            metadata={"trade_id": trade.id, "from_user": trade.from_user.id},
            before_quantity=before_qty,
            after_quantity=buyer_inv.quantity,
        )
        # Transfer currency from buyer to seller
        buyer_currency.balance -= total_price
        buyer_currency.save()
        seller_currency, _ = UserCurrency.objects.get_or_create(user=trade.from_user, currency=trade.currency, defaults={"balance": 0})
        before_bal = seller_currency.balance
        seller_currency.balance += net_to_seller
        seller_currency.save()
        # Log currency transactions
        CurrencyTransaction.objects.create(
            user=trade.to_user,
            currency=trade.currency,
            amount=-total_price,
            action="trade",
            source="trade",
            metadata={"trade_id": trade.id, "to_user": trade.from_user.id},
            before_balance=buyer_currency.balance + total_price,
            after_balance=buyer_currency.balance,
        )
        CurrencyTransaction.objects.create(
            user=trade.from_user,
            currency=trade.currency,
            amount=net_to_seller,
            action="trade",
            source="trade",
            metadata={"trade_id": trade.id, "from_user": trade.to_user.id, "fee": str(fee)},
            before_balance=before_bal,
            after_balance=seller_currency.balance,
        )
        # Mark trade as completed
        trade.status = 'completed'
        trade.save()
    return True
