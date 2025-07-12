
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from accounts.models import User, UserCurrency
from items.models import Item, InventoryItem
from transactions.models import InventoryTransaction, CurrencyTransaction
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta

@staff_member_required
def economy_dashboard(request):
    # Total currency in circulation by type
    currency_totals = UserCurrency.objects.values('currency').annotate(total=Sum('balance')).order_by('-total')
    # Top users by currency balance
    top_balances = UserCurrency.objects.values('user__email', 'currency').annotate(balance=Sum('balance')).order_by('-balance')[:10]
    # Top users by inventory quantity
    top_inventory = InventoryItem.objects.values('user__email').annotate(total_items=Sum('quantity')).order_by('-total_items')[:10]
    # Most traded items
    most_traded_items = InventoryTransaction.objects.values('item__name').annotate(trades=Count('id')).order_by('-trades')[:10]
    # Most valuable items (by base_price * quantity)
    item_values = InventoryItem.objects.values('item__name').annotate(
        total_value=Sum(F('quantity') * F('item__base_price'))
    ).order_by('-total_value')[:10]
    # Large transactions (over threshold)
    threshold = 1000  # Change as needed
    large_transactions = CurrencyTransaction.objects.filter(amount__gte=threshold).order_by('-timestamp')[:20]
    # Rapid/frequent changes (last 24h, more than N transactions)
    since = timezone.now() - timedelta(days=1)
    rapid_users = CurrencyTransaction.objects.filter(timestamp__gte=since).values('user__email').annotate(
        tx_count=Count('id')).filter(tx_count__gte=10).order_by('-tx_count')
    # Users with high balances or item quantities
    high_balances = UserCurrency.objects.filter(balance__gte=threshold).order_by('-balance')[:10]
    high_items = InventoryItem.objects.filter(quantity__gte=threshold).order_by('-quantity')[:10]
    # Recent admin adjustments
    recent_admin_adjustments = InventoryTransaction.objects.filter(action='admin').order_by('-timestamp')[:20]
    context = {
        'currency_totals': currency_totals,
        'top_balances': top_balances,
        'top_inventory': top_inventory,
        'most_traded_items': most_traded_items,
        'item_values': item_values,
        'large_transactions': large_transactions,
        'rapid_users': rapid_users,
        'high_balances': high_balances,
        'high_items': high_items,
        'recent_admin_adjustments': recent_admin_adjustments,
    }
    return render(request, 'admin/economy_dashboard.html', context)
