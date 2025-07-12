from django.contrib import admin
from .models import InventoryTransaction, CurrencyTransaction
from django.http import HttpResponse
import csv

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'action', 'source', 'timestamp', 'before_quantity', 'after_quantity')
    search_fields = ('user__email', 'item__name', 'action', 'source')
    ordering = ('-timestamp',)

@admin.register(CurrencyTransaction)
class CurrencyTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'amount', 'action', 'source', 'timestamp', 'before_balance', 'after_balance')
    search_fields = ('user__email', 'currency', 'action', 'source')
    ordering = ('-timestamp',)
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=currency_transactions.csv'
        writer = csv.writer(response)
        writer.writerow(['User', 'Currency', 'Amount', 'Action', 'Source', 'Timestamp', 'Before Balance', 'After Balance'])
        for obj in queryset:
            writer.writerow([
                obj.user.email,
                obj.currency,
                obj.amount,
                obj.action,
                obj.source,
                obj.timestamp,
                obj.before_balance,
                obj.after_balance
            ])
        return response
    export_as_csv.short_description = "Export selected transactions as CSV"
