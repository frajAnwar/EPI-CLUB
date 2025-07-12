from rest_framework import serializers
from .models import Event, Tournament, Round, Match, Participant, EventApplication
from teams.serializers import TeamSerializer

from django.utils import timezone

class EventSerializer(serializers.ModelSerializer):
    def validate(self, data):
        apply_until = data.get('apply_until', getattr(self.instance, 'apply_until', None))
        if apply_until and apply_until < timezone.now():
            raise serializers.ValidationError('The application deadline has already passed.')
        return data
    class Meta:
        model = Event
        fields = '__all__'

class MatchSerializer(serializers.ModelSerializer):
    team1 = TeamSerializer(read_only=True)
    team2 = TeamSerializer(read_only=True)
    winner = TeamSerializer(read_only=True)

    class Meta:
        model = Match
        fields = ('id', 'team1', 'team2', 'winner', 'score', 'is_completed')

class RoundSerializer(serializers.ModelSerializer):
    matches = MatchSerializer(many=True, read_only=True)

    class Meta:
        model = Round
        fields = ('id', 'round_number', 'name', 'is_completed', 'matches')

class ParticipantSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Participant
        fields = ('team', 'is_approved')

class TournamentSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True, source='participant_set')
    rounds = RoundSerializer(many=True, read_only=True)
    winner = TeamSerializer(read_only=True)

    def validate(self, data):
        apply_until = data.get('apply_until', getattr(self.instance, 'apply_until', None))
        if apply_until and apply_until < timezone.now():
            raise serializers.ValidationError('The application deadline has already passed.')
        return data

    class Meta:
        model = Tournament
        fields = ('id', 'name', 'game', 'start_date', 'end_date', 'apply_until', 'status', 'winner', 'participants', 'rounds')

class EventApplicationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    event = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EventApplication
        fields = [
            'id', 'event', 'user', 'info', 'status', 'attended', 'reward_granted', 'reward_xp', 'reward_currency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'attended', 'reward_granted', 'reward_xp', 'reward_currency', 'created_at', 'updated_at']
