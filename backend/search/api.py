from rest_framework import views, response, status
from django.db.models import Q
from accounts.models import User
from teams.models import Team
from events.models import Tournament
from accounts.serializers import UserProfileSerializer
from teams.serializers import TeamSerializer
from events.serializers import TournamentSerializer

class GlobalSearchView(views.APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')

        if not query:
            return response.Response(
                {'error': 'Query parameter "q" is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Search Users ---
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(full_name__icontains=query),
            is_approved=True
        ).distinct()

        # --- Search Teams ---
        teams = Team.objects.filter(
            Q(name__icontains=query) |
            Q(tag__icontains=query)
        ).distinct()

        # --- Search Tournaments ---
        tournaments = Tournament.objects.filter(name__icontains=query).distinct()

        # Serialize the results
        user_serializer = UserProfileSerializer(users, many=True)
        team_serializer = TeamSerializer(teams, many=True)
        tournament_serializer = TournamentSerializer(tournaments, many=True)

        return response.Response({
            'users': user_serializer.data,
            'teams': team_serializer.data,
            'tournaments': tournament_serializer.data,
        })
