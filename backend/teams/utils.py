from .models import Team
from django.contrib.auth import get_user_model
from django.db import models

def get_suggested_teams(user, limit=5):
    # Suggest teams with open slots, not already joined, prioritize teams with friends and similar games
    User = get_user_model()
    joined_team_ids = user.teams.values_list('id', flat=True)
    user_games = user.teams.values_list('game', flat=True)
    # Assume 'friends' are users the current user has chatted with (via ChatMessage)
    from .models import ChatMessage
    friend_ids = ChatMessage.objects.filter(user=user).values_list('recipient', flat=True).distinct()
    teams = Team.objects.exclude(id__in=joined_team_ids)
    # Prioritize teams with friends and same game
    teams = teams.annotate(
        num_members=models.Count('members'),
        has_friend=models.Case(
            models.When(members__id__in=friend_ids, then=1),
            default=0,
            output_field=models.IntegerField(),
        ),
        same_game=models.Case(
            models.When(game__in=user_games, then=1),
            default=0,
            output_field=models.IntegerField(),
        ),
    ).order_by('-has_friend', '-same_game', 'num_members')[:limit]
    return teams
