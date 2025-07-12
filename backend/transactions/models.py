from django.db import models
from accounts.models import User
from items.models import Item

class InventoryTransaction(models.Model):
    ACTION_CHOICES = [
        ("gain", "Gain"),
        ("use", "Use"),
        ("trade", "Trade"),
        ("loss", "Loss"),
        ("admin", "Admin Adjustment"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_transactions')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()  # Can be negative for use/loss
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    source = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    before_quantity = models.IntegerField()
    after_quantity = models.IntegerField()
    related_transaction = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.item.name} {self.action} {self.quantity} ({self.timestamp})"

class CurrencyTransaction(models.Model):
    ACTION_CHOICES = [
        ("gain", "Gain"),
        ("spend", "Spend"),
        ("trade", "Trade"),
        ("convert", "Convert"),
        ("admin", "Admin Adjustment"),
        ("reward", "Reward"),
        ("purchase", "Purchase"),
        ("burn", "Burn"),
        ("mint", "Mint"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='currency_transactions')
    from accounts.models import Currency
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    source = models.CharField(max_length=100, blank=True)  # e.g., 'shop', 'trade', 'quest', etc.
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    before_balance = models.DecimalField(max_digits=12, decimal_places=2)
    after_balance = models.DecimalField(max_digits=12, decimal_places=2)
    related_transaction = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.currency} {self.action} {self.amount} ({self.timestamp})"
