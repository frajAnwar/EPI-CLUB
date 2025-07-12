from rest_framework import serializers
from .models import Team

class ChangeTeamNameSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    tag = serializers.CharField(max_length=10)

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('created_by',)

class TeamMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
