from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    discord_id = models.CharField(max_length=64, unique=True, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    university_name = models.CharField(max_length=150, blank=True)
    gaming_interests = models.TextField(blank=True)
    motivation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    profile_banner = models.ImageField(upload_to='profile_banners/', blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    next_level_xp = models.PositiveIntegerField(default=1000)
    rank = models.CharField(max_length=13, default='E')
    talent_points = models.PositiveIntegerField(default=0)

    # Overall stats
    total_wins = models.PositiveIntegerField(default=0)
    total_losses = models.PositiveIntegerField(default=0)
    total_kills = models.PositiveIntegerField(default=0)
    total_deaths = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return self.email

    def get_team_tag(self):
        team = self.teams.first()
        return f"[{team.tag}]" if team else ""

# The Inventory model has been moved to the 'items' app for better organization.

# UserCurrency model for tracking user currency balances
class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='currency_icons/', blank=True, null=True)

    def __str__(self):
        return self.name

class UserCurrency(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='currencies')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user', 'currency')

    def __str__(self):
        return f"{self.user.email} - {self.currency.code}: {self.balance}"

from items.models import Item

class CurrencyConversionRate(models.Model):
    from_currency = models.ForeignKey('Currency', on_delete=models.CASCADE, related_name='conversion_from')
    to_currency = models.ForeignKey('Currency', on_delete=models.CASCADE, related_name='conversion_to')
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('from_currency', 'to_currency')

    def __str__(self):
        return f"1 {self.from_currency.code} = {self.rate} {self.to_currency.code}"

class Game(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    team_size = models.PositiveIntegerField(default=1)
    icon_url = models.URLField(blank=True, null=True)
    has_kd = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class UserGameStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_stats')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    stats = models.JSONField(default=dict)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f"{self.user.email} - {self.game.name} Stats"





class ActivityLog(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.timestamp}"


