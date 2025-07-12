from rest_framework import views, response
from django.db.models import Count
from accounts.models import User
from teams.models import Team
from events.models import Tournament
from accounts.serializers import UserProfileSerializer
from teams.serializers import TeamSerializer

class LeaderboardView(views.APIView):
    def get(self, request, *args, **kwargs):
        game_filter = self.request.query_params.get('game')
        period_filter = self.request.query_params.get('period')

        # --- User Leaderboard ---
        user_queryset = User.objects.filter(is_approved=True)
        if game_filter:
            # This assumes you have a way to link users to games, e.g., through a through model or a field on the user model.
            # For now, we'll filter by a hypothetical 'games_played' field.
            user_queryset = user_queryset.filter(games_played__name=game_filter)

        if period_filter == 'weekly':
            # Logic to filter by week
            pass
        elif period_filter == 'monthly':
            # Logic to filter by month
            pass

        top_users = user_queryset.order_by('-xp')[:10]

        # --- Team Leaderboard ---
        team_queryset = Team.objects.all()
        if game_filter:
            team_queryset = team_queryset.filter(game__name=game_filter)

        top_teams = team_queryset.annotate(
            num_wins=Count('matches_won', filter=models.Q(matches_won__tournament__status='completed'))
        ).order_by('-num_wins')[:10]

        # --- Valorant Leaderboard (Example) ---
        valorant_teams = Team.objects.filter(game__name='Valorant').annotate(
            num_wins=Count('matches_won', filter=models.Q(matches_won__tournament__status='completed'))
        ).order_by('-num_wins')[:10]

        # Serialize the results
        user_serializer = UserProfileSerializer(top_users, many=True)
        team_data = []
        for team in top_teams:
            team_serializer = TeamSerializer(team)
            data = team_serializer.data
            data['wins'] = team.num_wins
            team_data.append(data)

        valorant_team_data = []
        for team in valorant_teams:
            team_serializer = TeamSerializer(team)
            data = team_serializer.data
            data['wins'] = team.num_wins
            valorant_team_data.append(data)

        return response.Response({
            'users': user_serializer.data,
            'teams': team_data,
            'valorant': valorant_team_data,
        })
