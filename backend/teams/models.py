from django.db import models
from django.conf import settings

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    game = models.ForeignKey('accounts.Game', on_delete=models.CASCADE, related_name='teams')
    tag = models.CharField(max_length=10, unique=True, help_text="Short team tag (e.g. HNTR)")
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teams_created')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.game and self.members.count() > self.game.team_size:
            from django.core.exceptions import ValidationError
            raise ValidationError(f"Team for {self.game.name} cannot have more than {self.game.team_size} members.")

    def __str__(self):
        return f"[{self.tag}] {self.name} ({self.game.name})"

class ChatMessage(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} in {self.team.name}: {self.message[:20]}'

class TeamInvitation(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    invited_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='team_invitations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'invited_user')

    def __str__(self):
        return f'Invitation for {self.invited_user.username} to join {self.team.name}'
