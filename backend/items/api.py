
from rest_framework import serializers, generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Item, ItemCategory, InventoryItem
from transactions.models import CurrencyTransaction, InventoryTransaction
from accounts.models import UserCurrency
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from django.shortcuts import get_object_or_404
from notifications.utils import send_user_notification

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class InventoryItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    class Meta:
        model = InventoryItem
        fields = ['id', 'item', 'item_name', 'quantity', 'is_equipped', 'metadata']

class ShopItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'rarity', 'tradable', 'limited_edition', 'is_stackable']
    search_fields = ['name', 'description']
    ordering_fields = ['base_price', 'created_at', 'name']
    ordering = ['name']

class PurchaseItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        user = request.user
        item = get_object_or_404(Item, id=item_id)
        total_price = item.base_price * quantity
        # Assume default currency for now
        user_currency = UserCurrency.objects.filter(user=user).first()
        if not user_currency or user_currency.balance < total_price:
            return Response({'error': 'Insufficient balance.'}, status=status.HTTP_400_BAD_REQUEST)
        # Deduct currency
        before_balance = user_currency.balance
        user_currency.balance -= Decimal(total_price)
        user_currency.save()
        # Add to inventory
        inv_item, created = InventoryItem.objects.get_or_create(user=user, item=item, defaults={'quantity': 0})
        before_quantity = inv_item.quantity
        inv_item.quantity += quantity
        inv_item.save()
        # Log transactions
        CurrencyTransaction.objects.create(
            user=user,
            currency=user_currency.currency,
            amount=Decimal(total_price),
            action='purchase',
            source='shop',
            before_balance=before_balance,
            after_balance=user_currency.balance,
        )
        InventoryTransaction.objects.create(
            user=user,
            item=item,
            quantity=quantity,
            action='gain',
            source='shop',
            before_quantity=before_quantity,
            after_quantity=inv_item.quantity,
        )
        # Send notification to user
        message = f"You purchased {quantity}x {item.name} from the shop for {total_price} {user_currency.currency.name}."
        send_user_notification(user, message)
        return Response({'status': 'success', 'item': item.name, 'quantity': quantity})

class PurchaseHistoryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CurrencyTransaction
    def get_queryset(self):
        return CurrencyTransaction.objects.filter(user=self.request.user, action='purchase', source='shop').order_by('-timestamp')

class UserInventoryListView(generics.ListAPIView):
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return InventoryItem.objects.filter(user=self.request.user)
