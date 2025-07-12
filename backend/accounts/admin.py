from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Game, UserCurrency, CurrencyConversionRate
from teams.models import Team
from transactions.models import InventoryTransaction, CurrencyTransaction
from .forms import CustomUserCreationForm, CustomUserChangeForm




@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_size', 'description', 'icon_url')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag', 'game', 'created_by', 'created_at')
    search_fields = ('name', 'tag', 'description', 'game__name', 'created_by__email')
    filter_horizontal = ('members',)
    ordering = ('-created_at',)


from .models import Currency

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'icon')
    readonly_fields = ()

@admin.register(UserCurrency)
class UserCurrencyAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'balance')
    search_fields = ('user__email', 'currency')
    ordering = ('user', 'currency')

# Transaction admin now in transactions app

@admin.register(CurrencyConversionRate)
class CurrencyConversionRateAdmin(admin.ModelAdmin):
    list_display = ('from_currency', 'to_currency', 'rate', 'is_active', 'updated_at')
    list_filter = ('is_active', 'from_currency', 'to_currency')
    search_fields = ('from_currency__code', 'to_currency__code')
    ordering = ('from_currency', 'to_currency')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('id', 'email', 'username', 'level', 'rank', 'xp', 'next_level_xp', 'talent_points', 'is_approved', 'is_active', 'is_admin', 'date_joined')
    list_filter = ('is_approved', 'is_active', 'is_admin', 'rank', 'level')
    search_fields = ('email', 'username', 'discord_id', 'full_name', 'university_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'full_name', 'university_name', 'gaming_interests', 'motivation', 'discord_id', 'profile_pic')}),
        ('Game Stats', {'fields': ('level', 'xp', 'next_level_xp', 'rank', 'talent_points')}),
        ('Permissions', {'fields': ('is_active', 'is_approved', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'university_name', 'gaming_interests', 'motivation', 'discord_id', 'profile_pic', 'is_approved', 'is_active', 'is_admin', 'is_superuser', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('id', 'date_joined', 'last_login', 'level', 'xp', 'next_level_xp', 'rank', 'talent_points')




