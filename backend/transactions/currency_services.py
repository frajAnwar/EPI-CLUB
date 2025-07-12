from django.db import transaction
from accounts.models import UserCurrency
from transactions.models import CurrencyTransaction
from decimal import Decimal

def convert_currency(user, from_currency, to_currency, amount, conversion_rate):
    """
    Convert currency for a user from one type to another at a given rate.
    Logs both the deduction and the addition as CurrencyTransaction.
    """
    if amount <= 0:
        raise ValueError("Amount must be positive.")
    with transaction.atomic():
        from_uc = UserCurrency.objects.select_for_update().get(user=user, currency=from_currency)
        to_uc, _ = UserCurrency.objects.select_for_update().get_or_create(user=user, currency=to_currency, defaults={"balance": 0})
        if from_uc.balance < amount:
            raise ValueError("Insufficient funds to convert.")
        from_before = from_uc.balance
        to_before = to_uc.balance
        from_uc.balance -= amount
        to_uc.balance += Decimal(amount) * Decimal(conversion_rate)
        from_uc.save()
        to_uc.save()
        CurrencyTransaction.objects.create(
            user=user,
            currency=from_currency,
            amount=-amount,
            action="convert",
            source="conversion",
            metadata={"to_currency": to_currency.code, "rate": str(conversion_rate)},
            before_balance=from_before,
            after_balance=from_uc.balance,
        )
        CurrencyTransaction.objects.create(
            user=user,
            currency=to_currency,
            amount=Decimal(amount) * Decimal(conversion_rate),
            action="convert",
            source="conversion",
            metadata={"from_currency": from_currency.code, "rate": str(conversion_rate)},
            before_balance=to_before,
            after_balance=to_uc.balance,
        )
    return True

def mint_currency(user, currency, amount, reason="admin_mint"):
    """
    Admin function to add currency to a user's balance.
    """
    if amount <= 0:
        raise ValueError("Amount must be positive.")
    with transaction.atomic():
        uc, _ = UserCurrency.objects.select_for_update().get_or_create(user=user, currency=currency, defaults={"balance": 0})
        before = uc.balance
        uc.balance += amount
        uc.save()
        CurrencyTransaction.objects.create(
            user=user,
            currency=currency,
            amount=amount,
            action="mint",
            source=reason,
            metadata={},
            before_balance=before,
            after_balance=uc.balance,
        )
    return True

def burn_currency(user, currency, amount, reason="admin_burn"):
    """
    Admin function to remove currency from a user's balance.
    """
    if amount <= 0:
        raise ValueError("Amount must be positive.")
    with transaction.atomic():
        uc = UserCurrency.objects.select_for_update().get(user=user, currency=currency)
        if uc.balance < amount:
            raise ValueError("Insufficient funds to burn.")
        before = uc.balance
        uc.balance -= amount
        uc.save()
        CurrencyTransaction.objects.create(
            user=user,
            currency=currency,
            amount=-amount,
            action="burn",
            source=reason,
            metadata={},
            before_balance=before,
            after_balance=uc.balance,
        )
    return True
