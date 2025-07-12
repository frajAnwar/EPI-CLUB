from django.db import models
from django.conf import settings
from accounts.models import Game
from teams.models import Team

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    apply_until = models.DateTimeField(null=True, blank=True, help_text="Deadline for applications")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='attended_events', blank=True)
    status = models.CharField(max_length=20, choices=[('upcoming', 'Upcoming'), ('live', 'Live'), ('completed', 'Completed'), ('archived', 'Archived'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='upcoming')

    def __str__(self):
        return self.name

class Tournament(models.Model):
    name = models.CharField(max_length=200)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='tournaments', null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    apply_until = models.DateTimeField(null=True, blank=True, help_text="Deadline for team applications")
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    participants = models.ManyToManyField(Team, blank=True, through='Participant')
    status = models.CharField(max_length=20, choices=[('upcoming', 'Upcoming'), ('live', 'Live'), ('completed', 'Completed'), ('archived', 'Archived'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('in_progress', 'In Progress')], default='upcoming')
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='tournaments_won')
    reward_currency = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Participant(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'tournament')

    def __str__(self):
        return f'{self.team.name} in {self.tournament.name}'

class Round(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.PositiveIntegerField()
    name = models.CharField(max_length=100, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('tournament', 'round_number')

    def __str__(self):
        return f'Round {self.round_number} of {self.tournament.name}'

class Match(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='matches')
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2', null=True, blank=True) # Can be null for byes
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name='matches_won', null=True, blank=True)
    score = models.CharField(max_length=50, blank=True)
    match_time = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f'Match {self.id} in {self.round.tournament.name}'

class TournamentAttendanceReward(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='attendance_rewards')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tournament_rewards')
    xp = models.IntegerField(null=True, blank=True)
    currency = models.IntegerField(null=True, blank=True)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tournament', 'user')

    def __str__(self):
        return f'Reward for {self.user.username} in {self.tournament.name}'

class EventApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_applications')
    info = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    attended = models.BooleanField(default=False)
    reward_granted = models.BooleanField(default=False)
    reward_xp = models.IntegerField(null=True, blank=True)
    reward_currency = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f'{self.user.username} application for {self.event.name}'
