from django.contrib import admin
from .models import Item, ItemCategory, InventoryItem

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'is_equipped', 'metadata')
    search_fields = ('user__username', 'item__name', 'metadata')
    list_filter = ('is_equipped', 'item__categories', 'item__rarity')
    list_select_related = ('user', 'item')
    raw_id_fields = ('user', 'item')

@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'rarity', 'tradable', 'limited_edition', 'base_price', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('rarity', 'tradable', 'limited_edition', 'categories')
    filter_horizontal = ('categories',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'rarity', 'icon')
        }),
        ('Stats', {
            'fields': ('power', 'base_price')
        }),
        ('Behavior', {
            'fields': ('tradable', 'limited_edition', 'admin_approval_required', 'is_stackable', 'max_per_user')
        }),
        ('Categorization', {
            'fields': ('categories',)
        }),
    )
