from rest_framework import viewsets
from .models import Trade, Auction, Bid
from .serializers import TradeSerializer, AuctionSerializer, BidSerializer
from notifications.utils import send_group_notification, send_user_notification
from accounts.models import User

class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.select_related('item1', 'item2', 'user1', 'user2').all()
    serializer_class = TradeSerializer
    search_fields = ['item1__name', 'item2__name', 'user1__username', 'user2__username', 'status']
    filterset_fields = ['item1', 'item2', 'user1', 'user2', 'status']

    def perform_create(self, serializer):
        trade = serializer.save(user1=self.request.user)
        send_user_notification(trade.user2, f"You have a new trade offer from {trade.user1.username}")
        if trade.item1.admin_approval_required or trade.item2.admin_approval_required:
            admins = User.objects.filter(is_admin=True)
            message = f"A new trade involving a high-value item requires your approval."
            send_group_notification(admins, message)

class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.select_related('item', 'seller').all()
    serializer_class = AuctionSerializer
    search_fields = ['item__name', 'seller__username', 'status']
    filterset_fields = ['item', 'seller', 'status', 'current_price', 'end_time']

    def perform_create(self, serializer):
        auction = serializer.save(seller=self.request.user)
        # Notify followers of the item or seller

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.select_related('auction', 'bidder').all()
    serializer_class = BidSerializer

    def perform_create(self, serializer):
        bid = serializer.save(bidder=self.request.user)
        send_user_notification(bid.auction.seller, f"You have a new bid on your auction for {bid.auction.item.name}")
        # Notify previous high bidder
        previous_high_bid = bid.auction.bid_set.order_by('-amount').first()
        if previous_high_bid and previous_high_bid.bidder != bid.bidder:
            send_user_notification(previous_high_bid.bidder, f"You have been outbid on the auction for {bid.auction.item.name}")
