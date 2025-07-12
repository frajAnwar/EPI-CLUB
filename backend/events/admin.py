from django.contrib import admin
from .models import Event, Tournament

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'created_by')
    search_fields = ('name', 'description')
    list_filter = ('start_time', 'end_time', 'created_by')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'start_date', 'end_date', 'organizer')
    search_fields = ('name', 'game__name')
    list_filter = ('game', 'start_date', 'end_date', 'organizer')
