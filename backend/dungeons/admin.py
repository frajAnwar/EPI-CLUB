from django.contrib import admin
from .models import Dungeon, Entity, DungeonRun, WorldZone,  PlayerDungeonState, EntityCategory


@admin.register(Dungeon)
class DungeonAdmin(admin.ModelAdmin):
    list_display = ('name', 'rank', 'min_level', 'max_level', 'is_active', 'zone')
    search_fields = ('name', 'description', 'zone__name', 'tags')
    list_filter = ('rank', 'is_active', 'zone')
    filter_horizontal = ('item_categories', 'entity_categories')
    autocomplete_fields = ('zone',)
    search_fields = ('name', 'description', 'zone__name')

@admin.register(EntityCategory)
class EntityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'entity_type', 'power', 'image_url')
    search_fields = ('name', 'description')
    list_filter = ('entity_type', 'categories')
    filter_horizontal = ('categories', 'loot_categories')


@admin.register(DungeonRun)
class DungeonRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'dungeon', 'current_floor', 'status', 'start_time', 'end_time')
    search_fields = ('user__email', 'dungeon__name')
    list_filter = ('dungeon', 'status')




@admin.register(PlayerDungeonState)
class PlayerDungeonStateAdmin(admin.ModelAdmin):
    list_display = ('user', 'max_anima', 'daily_gates_entered', 'last_daily_reset')
    search_fields = ('user__email',)


# WORLD EVENTS
from .models import WorldEvent, WorldEventEffect, EventEffectApplication, ActiveWorldEvent

class DungeonInline(admin.TabularInline):
    model = Dungeon
    verbose_name = "Assigned Dungeon"
    verbose_name_plural = "Assigned Dungeons (Informational Only)"
    extra = 0
    fields = ('name', 'rank', 'is_active')
    readonly_fields = fields
    show_change_link = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(WorldZone)
class WorldZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'rank_pool', 'world_map_x', 'world_map_y')
    list_editable = ('world_map_x', 'world_map_y')
    search_fields = ('name',)
    list_filter = ('is_saturated',)
    inlines = [DungeonInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'rank_pool')
        }),
        ('Map Details', {
            'fields': ('world_map_x', 'world_map_y', 'background_image')
        }),
        ('State', {
            'fields': ('is_saturated', 'is_infested', 'saturation_expires_at')
        }),
    )

# ========== WORLD EVENT ADMIN ==========
class EventEffectApplicationInline(admin.TabularInline):
    model = EventEffectApplication
    extra = 1
    autocomplete_fields = ('effect',)

@admin.register(WorldEvent)
class WorldEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'identifier', 'event_type', 'duration_hours')
    list_filter = ('event_type',)
    search_fields = ('name', 'identifier')
    inlines = [EventEffectApplicationInline]  # Replaced filter_horizontal

@admin.register(WorldEventEffect)
class WorldEventEffectAdmin(admin.ModelAdmin):
    list_display = ('name', 'identifier', 'effect_type')
    list_filter = ('effect_type',)
    search_fields = ('name', 'identifier')

@admin.register(EventEffectApplication)
class EventEffectApplicationAdmin(admin.ModelAdmin):
    list_display = ('event', 'effect', 'weight')
    list_filter = ('event', 'effect')
    autocomplete_fields = ('event', 'effect')

# ========== ACTIVE WORLD EVENT ADMIN ==========
@admin.register(ActiveWorldEvent)
class ActiveWorldEventAdmin(admin.ModelAdmin):
    list_display = ('event', 'zone', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active', 'event', 'zone')
    readonly_fields = ('start_time',)
    autocomplete_fields = ('event', 'zone')

from .models import TacticalApproach

@admin.register(TacticalApproach)
class TacticalApproachAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'description')
    list_filter = ('category',)