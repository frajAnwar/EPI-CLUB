from django.db import models

class ItemCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Item(models.Model):
    RARITY_CHOICES = [
        ('common', 'Common (C)'),
        ('uncommon', 'Uncommon (U)'),
        ('rare', 'Rare (R)'),
        ('epic', 'Epic (E)'),
        ('legendary', 'Legendary (L)'),
        ('mythic', 'Mythic (M)'),
        ('relic', 'Relic (Re)'),
        ('masterwork', 'Masterwork (Ma)'),
        ('eternal', 'Eternal (Et)'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    power = models.PositiveIntegerField(default=0, help_text="The power bonus this item provides, if any.")
    tradable = models.BooleanField(default=True)
    limited_edition = models.BooleanField(default=False)
    admin_approval_required = models.BooleanField(default=False)
    icon = models.ImageField(upload_to='item_icons/', blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_per_user = models.PositiveIntegerField(default=99, help_text="Maximum number of this item a user can hold.")
    is_stackable = models.BooleanField(default=True, help_text="Can multiple instances of this item stack in the inventory?")
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(ItemCategory, blank=True, related_name='items')

    def __str__(self):
        return f"{self.name} ({self.rarity})"

from django.conf import settings

class InventoryItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventory')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='in_inventories')
    quantity = models.PositiveIntegerField(default=1)
    is_equipped = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True, help_text='For storing unique item data like enhancements, origin, etc.')

    class Meta:
        # This constraint ensures a user can only have one equipped instance of an item.
        # A user can have multiple unequipped instances.
        constraints = [
            models.UniqueConstraint(fields=['user', 'item'], condition=models.Q(is_equipped=True), name='unique_equipped_item')
        ]

    def __str__(self):
        equipped_status = "[Equipped]" if self.is_equipped else ""
        return f"{self.user.username} - {self.item.name} (x{self.quantity}) {equipped_status}"
