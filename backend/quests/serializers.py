from rest_framework import serializers
from .models import Quest, UserQuest

class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = '__all__'

class UserQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuest
        fields = '__all__'
        read_only_fields = ('user',)
