from django.db import models
from accounts.models import User, Item

# ShopItem for admin/global shop (fixed prices)
class ShopItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='shop_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, choices=[('game', 'GameCoin'), ('club', 'ClubCoin')])
    stock = models.PositiveIntegerField(default=0)
    is_flash_sale = models.BooleanField(default=False)
    sale_start = models.DateTimeField(blank=True, null=True)
    sale_end = models.DateTimeField(blank=True, null=True)
    is_limited_time = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.item.name} - {self.price} {self.currency}"

# Trade model for player-to-player trades (player sets price)
class Trade(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades_offered')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades_received')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='trades')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, choices=[('game', 'GameCoin'), ('club', 'ClubCoin')])
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('completed', 'Completed')], default='pending')
    admin_approval = models.BooleanField(default=False)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trade: {self.from_user.email} -> {self.to_user.email} | {self.item.name} x{self.quantity} for {self.price} {self.currency}"

class Auction(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='auctions')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions_created')
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    end_time = models.DateTimeField()
    highest_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    highest_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auctions_won')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Auction for {self.item.name} by {self.seller.email}"

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids_placed')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid of {self.amount} on {self.auction.item.name} by {self.bidder.email}"
