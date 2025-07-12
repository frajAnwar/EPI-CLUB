from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'read', 'created_at')
    search_fields = ('recipient__username', 'message')
    list_filter = ('read', 'created_at')
