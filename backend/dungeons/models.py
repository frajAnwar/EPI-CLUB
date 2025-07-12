from django.core.exceptions import ValidationError
from django.db import models
from accounts.models import User
from items.models import ItemCategory

class EntityCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


DUNGEON_RANK_CHOICES = [
    ('E', 'E-Rank'),
    ('D', 'D-Rank'),
    ('C', 'C-Rank'),
    ('B', 'B-Rank'),
    ('A', 'A-Rank'),
    ('S', 'S-Rank'),
    ('SS', 'SS-Rank'),
    ('SSS', 'SSS-Rank'),
    ('National', 'National-Rank'),
]
class Dungeon(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    rank = models.CharField(max_length=13, choices=DUNGEON_RANK_CHOICES, default='E')
    min_level = models.PositiveIntegerField(default=1)
    max_level = models.PositiveIntegerField(default=100)
    tags = models.JSONField(default=list, blank=True, help_text='e.g., ["Cave", "Undead", "Cursed"]')
    is_active = models.BooleanField(default=True)
    item_categories = models.ManyToManyField(ItemCategory, related_name='dungeons', help_text='The item categories that can drop in this dungeon.')
    entity_categories = models.ManyToManyField(EntityCategory, related_name='dungeons', help_text='The entity categories that can spawn in this dungeon.')
    zone_map_x = models.PositiveIntegerField(default=0, help_text="Position within the zone's 1920x1080 map.")
    zone_map_y = models.PositiveIntegerField(default=0, help_text="Position within the zone's 1920x1080 map.")
    icon = models.ImageField(upload_to='dungeon_icons/', blank=True, null=True)
    # --- New fields for anomaly/instability ---
    instability_level = models.PositiveIntegerField(default=0, help_text='0-100, triggers anomaly at 100')
    anomaly_state = models.CharField(max_length=50, blank=True, help_text='e.g., "Swarm", "Elite", "Volatile"')
    anomaly_active_until = models.DateTimeField(blank=True, null=True)
    zone = models.ForeignKey('WorldZone', on_delete=models.SET_NULL, null=True, blank=True, related_name='dungeons')
    world_events = models.ManyToManyField(
        'WorldEvent',
        blank=True,
        help_text='Events that can trigger in this dungeon'
    )
    
    def get_active_modifiers(self):
        from dungeons.services import WorldEventService  # Add absolute import
        context = {
            'dungeon': self,
            'zone': self.zone
        }
        return WorldEventService.apply_effects(context, 'combat')

    def __str__(self):
        return self.name


class Entity(models.Model):
    ENTITY_TYPE_CHOICES = [
        ('minion', 'Minion'),
        ('boss', 'Boss'),
        ('final_boss', 'Final Boss'),
    ]
    name = models.CharField(max_length=100)
    rank = models.CharField(max_length=13, choices=DUNGEON_RANK_CHOICES, default='E')
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES, default='minion')
    categories = models.ManyToManyField(EntityCategory, related_name='entities', help_text='The categories this entity belongs to.')
    image_url = models.URLField(blank=True, null=True, help_text='Frontend image or identifier')
    power = models.PositiveIntegerField(default=1, help_text="The numerical power level of the entity.")
    min_xp = models.PositiveIntegerField(default=10, help_text="Minimum XP gained for defeating this entity.")
    max_xp = models.PositiveIntegerField(default=20, help_text="Maximum XP gained for defeating this entity.")
    min_coins = models.PositiveIntegerField(default=5, help_text="Minimum coins dropped by this entity.")
    max_coins = models.PositiveIntegerField(default=15, help_text="Maximum coins dropped by this entity.")
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True, help_text='List of tags for quest/objective detection, e.g., ["goblin", "beast"]')
    loot_categories = models.ManyToManyField('items.ItemCategory', related_name='entities', blank=True, help_text='The item categories that can drop from this entity.')

    def __str__(self):
        return f"{self.name} ({self.rank}) - {self.entity_type}"




class PlayerScoutingData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scouting_data')
    dungeon = models.ForeignKey(Dungeon, on_delete=models.CASCADE, related_name='scouting_data')
    stage = models.PositiveIntegerField(default=0)  # 0 = not scouted, 1 = basic, 2 = anomaly/loot, 3 = boss/rares
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'dungeon')

class PlayerDungeonState(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='dungeon_state')
    max_anima = models.PositiveIntegerField(default=3, help_text="Player's maximum Anima.")
    daily_gates_entered = models.PositiveIntegerField(default=0)
    last_daily_reset = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Dungeon State"

class PlayerGate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_gates')
    dungeon = models.ForeignKey(Dungeon, on_delete=models.CASCADE, related_name='player_gates')
    day = models.DateField(auto_now_add=True)
    map_x = models.PositiveIntegerField()
    map_y = models.PositiveIntegerField()
    is_completed = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)
    total_floors = models.PositiveIntegerField()
    encounter_log = models.JSONField(default=list)

    class Meta:
        unique_together = ('user', 'dungeon', 'day')

    def __str__(self):
        return f"{self.user.email}'s {self.dungeon.name} gate for {self.day}"

class DungeonRun(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'), # In the Sanctuary, making a choice for the next floor
        ('advancing', 'Advancing'),     # An encounter timer is active
        ('encounter_resolved', 'Encounter Resolved'), # Paused after a single encounter
        ('floor_completed', 'Floor Completed'), # Paused after the last encounter of a floor
        ('completed', 'Completed'), # Entire dungeon is done
        ('failed', 'Failed'),
        ('abandoned', 'Abandoned'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dungeon_runs')
    dungeon = models.ForeignKey(Dungeon, on_delete=models.CASCADE, related_name='runs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    anima = models.PositiveIntegerField(default=3, help_text="The player's remaining lives for this expedition.")
    current_floor = models.PositiveIntegerField(default=1)
    current_encounter_index = models.PositiveIntegerField(default=0)
    floor_completion_time = models.DateTimeField(blank=True, null=True)
    total_floors = models.PositiveIntegerField(default=1)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    rewards = models.JSONField(default=dict, help_text='All rewards for this run')
    tactical_approach_log = models.JSONField(default=list, blank=True, help_text='A log of the tactical choices made by the player.')
    encounter_log = models.JSONField(default=list, blank=True, help_text='A detailed log of each encounter.')
    unclaimed_rewards = models.JSONField(default=list, blank=True, help_text='A list of rewards that have not yet been claimed by the player.')
    last_floor_results = models.JSONField(default=dict, blank=True, help_text='DEPRECATED: The results of the most recently completed floor.')
    last_encounter_result = models.JSONField(default=dict, blank=True, help_text='The result of the most recently resolved encounter.')
    active_modifiers = models.JSONField(default=list, blank=True, help_text='A list of active modifiers from tactical approaches.')
    # --- New fields for provisions, critical events, anomaly ---
    provisions_used = models.JSONField(default=list, blank=True, help_text='List of provision item IDs used for this run')
    critical_events = models.JSONField(default=list, blank=True, help_text='List of critical events (with status/choices) for this run')
    anomaly_state = models.CharField(max_length=50, blank=True, help_text='e.g., "Swarm", "Elite", "Volatile"')

    def __str__(self):
        return f"{self.user.email} - {self.dungeon.name} Run ({self.status})"


# --- New Models for Phase 1 ---
class WorldZone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    world_map_x = models.PositiveIntegerField(default=0, help_text="Position on the main world map.")
    world_map_y = models.PositiveIntegerField(default=0, help_text="Position on the main world map.")
    background_image = models.ImageField(upload_to='zone_backgrounds/', blank=True, null=True, help_text="1920x1080 background image for the zone.")
    is_saturated = models.BooleanField(default=False)
    is_infested = models.BooleanField(default=False)
    saturation_expires_at = models.DateTimeField(blank=True, null=True)
    rank_pool = models.JSONField(default=list, blank=True, help_text='A list of ranks that can spawn in this zone, e.g., ["E", "D"]')

    def __str__(self):
        return self.name

class HallOfFame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hall_of_fame_entries')
    achievement = models.CharField(max_length=255)
    date_earned = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.achievement}"

class LegacyTrait(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    effect = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

class UserLegacyTrait(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='legacy_traits')
    trait = models.ForeignKey(LegacyTrait, on_delete=models.CASCADE, related_name='users')
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'trait')

    def __str__(self):
        return f"{self.user.email} - {self.trait.name}"


class Talent(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    tree = models.CharField(max_length=50) # e.g., 'The Eye of the Observer'
    max_rank = models.PositiveIntegerField(default=5)
    rank_bonuses = models.JSONField(default=list) # e.g., [{"stat": "scout_cost_redux", "value": 0.03}, ...]
    required_rank = models.CharField(max_length=13, choices=DUNGEON_RANK_CHOICES, default='E')
    required_talents = models.ManyToManyField('self', blank=True, symmetrical=False)

    def __str__(self):
        return f"{self.tree} - {self.name}"

class UserTalent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='talents')
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE, related_name='users')
    rank = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'talent')

    def __str__(self):
        return f"{self.user.email} - {self.talent.name} (Rank {self.rank})"


class ShopItem(models.Model):
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE)
    cost_game_coin = models.PositiveIntegerField(default=0)
    cost_club_coin = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=100)
    is_hunter_supply = models.BooleanField(default=False)
    is_club_store = models.BooleanField(default=False)

    def __str__(self):
        return self.item.name


class MarketplaceListing(models.Model):
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} by {self.seller.email}"

# Add to models.py
class WorldEventEffect(models.Model):
    EFFECT_TYPE_CHOICES = [
        ('DAMAGE_MOD', 'Damage Modifier'),
        ('LOOT_MOD', 'Loot Modifier'),
        ('XP_MOD', 'XP Modifier'),
        ('CURRENCY_MOD', 'Currency Modifier'),
        ('SPAWN_MOD', 'Spawn Modifier'),
        ('ENVIRONMENT', 'Environmental Effect'),
        ('SPECIAL', 'Special Effect'),
    ]
    identifier = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    effect_type = models.CharField(max_length=20, choices=EFFECT_TYPE_CHOICES)
    parameters = models.JSONField(default=dict)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.effect_type})"

class WorldEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('ENVIRONMENTAL', 'Environmental Event'),
        ('ROAMING_BOSS', 'Roaming Boss'),
        ('DUNGEON_BREAK', 'Dungeon Break'),
        ('ZONE_SATURATION', 'Zone Saturation'),
        ('SPECIAL', 'Special Event'),
    ]
    identifier = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    duration_hours = models.PositiveIntegerField(default=24)
    cooldown_hours = models.PositiveIntegerField(default=72)
    activation_conditions = models.JSONField(default=dict)
    effects = models.ManyToManyField(WorldEventEffect, through='EventEffectApplication')
    icon = models.CharField(max_length=100, blank=True)
    map_icon = models.TextField(blank=True, help_text="SVG content for the map icon")

    def __str__(self):
        return self.name

class EventEffectApplication(models.Model):
    event = models.ForeignKey(WorldEvent, on_delete=models.CASCADE)
    effect = models.ForeignKey(WorldEventEffect, on_delete=models.CASCADE)
    parameters = models.JSONField(default=dict)
    weight = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('event', 'effect')

    def __str__(self):
        return f"{self.event.name} → {self.effect.name}"

class ActiveWorldEvent(models.Model):
    event = models.ForeignKey(WorldEvent, on_delete=models.CASCADE)
    zone = models.ForeignKey(WorldZone, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    current_state = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.event.name} in {self.zone.name}"

class EventTriggerHistory(models.Model):
    event = models.ForeignKey(WorldEvent, on_delete=models.CASCADE)
    zone = models.ForeignKey(WorldZone, on_delete=models.CASCADE)
    triggered_at = models.DateTimeField(auto_now_add=True)
    triggered_by = models.CharField(max_length=50)  # 'system', 'player', 'quest'
    details = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.event.name} triggered at {self.triggered_at}"


class TacticalApproach(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, help_text="e.g., Brute Force, Economic, High-Risk")
    description = models.TextField()
    effects = models.JSONField(default=dict, help_text="The detailed effects block for this approach.")

    def __str__(self):
        return f"{self.category} - {self.name}"