# services.py
from datetime import timedelta
import random
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from items.models import Item
from accounts.models import UserCurrency
from dungeons.models import (
    WorldEvent, WorldEventEffect, ActiveWorldEvent, 
    WorldZone, Dungeon, EventEffectApplication
)

class WorldEventService:
    @staticmethod
    def get_active_events(zone=None):
        now = timezone.now()
        qs = ActiveWorldEvent.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_active=True
        )
        if zone:
            qs = qs.filter(zone=zone)
        return qs
    
    @staticmethod
    def apply_effects(context, target_type):
        modifiers = {}
        zone = context.get('zone')
        active_events = WorldEventService.get_active_events(zone=zone)
        
        for active_event in active_events:
            for effect_app in active_event.event.eventeffectapplication_set.all():
                effect = effect_app.effect
                params = {**effect.parameters, **effect_app.parameters}
                
                # Apply effect based on type
                if effect.effect_type == 'DAMAGE_MOD' and target_type == 'combat':
                    if params.get('target') == 'player':
                        modifiers.setdefault('player_damage_mod', 0)
                        modifiers['player_damage_mod'] += params['value']
                    elif params.get('target') == 'enemy':
                        modifiers.setdefault('enemy_damage_mod', 0)
                        modifiers['enemy_damage_mod'] += params['value']
                
                elif effect.effect_type == 'LOOT_MOD' and target_type == 'loot':
                    modifiers.setdefault('drop_rate_mod', {})
                    for rarity, value in params['rarity_rates'].items():
                        modifiers['drop_rate_mod'].setdefault(rarity, 0)
                        modifiers['drop_rate_mod'][rarity] += value
                
                elif effect.effect_type == 'ENVIRONMENT' and target_type == 'environment':
                    modifiers.setdefault('environmental_effects', [])
                    modifiers['environmental_effects'].append({
                        'name': effect.name,
                        'key': effect.identifier,
                        **params
                    })
        
        return modifiers

    @staticmethod
    def trigger_event(event_identifier, zone, triggered_by='system', details=None):
        try:
            event = WorldEvent.objects.get(identifier=event_identifier)
            now = timezone.now()
            end_time = now + timedelta(hours=event.duration_hours)
            
            active_event = ActiveWorldEvent.objects.create(
                event=event,
                zone=zone,
                end_time=end_time
            )
            
            return active_event
        except WorldEvent.DoesNotExist:
            return False
