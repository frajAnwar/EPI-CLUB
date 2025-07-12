from django.contrib import admin
from .models import Quest, UserQuest

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'reward_xp', 'reward_currency', 'is_real_world')
    search_fields = ('title', 'description')
    list_filter = ('is_real_world',)

@admin.register(UserQuest)
class UserQuestAdmin(admin.ModelAdmin):
    list_display = ('user', 'quest', 'is_completed', 'completed_at')
    search_fields = ('user__username', 'quest__title')
    list_filter = ('is_completed',)
