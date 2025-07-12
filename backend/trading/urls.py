from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import TradeViewSet, AuctionViewSet, BidViewSet

router = DefaultRouter()
router.register(r'trades', TradeViewSet)
router.register(r'auctions', AuctionViewSet)
router.register(r'bids', BidViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
