from django.contrib import admin
from .models import ShopItem, Trade

@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'price', 'currency', 'stock', 'is_flash_sale', 'sale_start', 'sale_end', 'is_limited_time')
    list_filter = ('currency', 'is_flash_sale', 'is_limited_time')
    search_fields = ('item__name',)
    ordering = ('-sale_start',)

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'item', 'quantity', 'price', 'currency', 'status', 'admin_approval', 'fee', 'created_at')
    list_filter = ('currency', 'status', 'admin_approval')
    search_fields = ('from_user__email', 'to_user__email', 'item__name')
    ordering = ('-created_at',)
