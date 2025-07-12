from rest_framework import serializers
from .models import User, Game, ActivityLog, UserGameStats

class SetUsernameSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        from .models import User
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

class ChangeUsernameSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)

class BanUserSerializer(serializers.Serializer):
    is_banned = serializers.BooleanField()

class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_approved', 'is_admin', 'is_banned']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'

class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ActivityLog
        fields = ('user', 'action', 'details', 'timestamp')

class UserApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_approved']

class UserGameStatsSerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = UserGameStats
        fields = ('game', 'stats')

class UserProfileSerializer(serializers.ModelSerializer):
    teams = serializers.SerializerMethodField()
    achievements = serializers.SerializerMethodField()
    game_stats = UserGameStatsSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'full_name', 'profile_pic', 'level', 'xp', 'rank',
            'total_wins', 'total_losses', 'total_kills', 'total_deaths',
            'teams', 'achievements', 'currencies', 'game_stats'
        )

    def get_teams(self, obj):
        from teams.serializers import TeamSerializer
        return TeamSerializer(obj.teams.all(), many=True).data

    def get_achievements(self, obj):
        from achievements.serializers import UserAchievementSerializer
        return UserAchievementSerializer(obj.user_achievements.filter(displayed=True), many=True).data
