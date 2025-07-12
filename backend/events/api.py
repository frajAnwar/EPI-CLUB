from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Event, Tournament, Match, Participant, EventApplication
from .serializers import EventSerializer, TournamentSerializer, MatchSerializer, ParticipantSerializer, EventApplicationSerializer
from .filters import EventFilter, TournamentFilter
from notifications.utils import send_user_notification, send_group_notification
from accounts.models import User

from django.utils import timezone

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related('created_by').prefetch_related('attendees').all()
    serializer_class = EventSerializer
    filterset_class = EventFilter
    search_fields = ['name', 'description', 'status']
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        event = serializer.save(created_by=self.request.user)
        # No need to notify admins, only admins can create events now

    def get_queryset(self):
        queryset = Event.objects.all()
        now = timezone.now()
        # Auto-update status based on time
        for event in queryset:
            if event.end_time and now > event.end_time and event.status != 'completed':
                event.status = 'completed'
                event.save(update_fields=['status'])
            elif event.start_time and now >= event.start_time and (not event.end_time or now <= event.end_time) and event.status != 'live':
                event.status = 'live'
                event.save(update_fields=['status'])
            elif event.start_time and now < event.start_time and event.status != 'upcoming':
                event.status = 'upcoming'
                event.save(update_fields=['status'])
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        event = self.get_object()
        user = request.user
        info = request.data.get('info', {})
        if event.apply_until and timezone.now() > event.apply_until:
            return Response({'error': 'Application deadline has passed.'}, status=status.HTTP_400_BAD_REQUEST)
        if EventApplication.objects.filter(event=event, user=user).exists():
            return Response({'error': 'You have already applied to this event.'}, status=status.HTTP_400_BAD_REQUEST)
        app = EventApplication.objects.create(event=event, user=user, info=info)
        # Notify admins
        admins = User.objects.filter(is_admin=True)
        for admin in admins:
            send_user_notification(admin, f"New application for event '{event.name}' from {user.username}.")
        send_user_notification(user, f"You have successfully applied to the event: {event.name}")
        return Response(EventApplicationSerializer(app).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[IsAdminUser])
    def applications(self, request, pk=None):
        event = self.get_object()
        apps = event.applications.all()
        serializer = EventApplicationSerializer(apps, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='applications/(?P<app_id>[^/.]+)/approve', permission_classes=[IsAdminUser])
    def approve_application(self, request, pk=None, app_id=None):
        event = self.get_object()
        try:
            app = EventApplication.objects.get(id=app_id, event=event)
        except EventApplication.DoesNotExist:
            return Response({'error': 'Application not found.'}, status=status.HTTP_404_NOT_FOUND)
        app.status = 'approved'
        app.save()
        send_user_notification(app.user, f"Your application for event '{event.name}' has been approved!")
        return Response(EventApplicationSerializer(app).data)

    @action(detail=True, methods=['post'], url_path='applications/(?P<app_id>[^/.]+)/reject', permission_classes=[IsAdminUser])
    def reject_application(self, request, pk=None, app_id=None):
        event = self.get_object()
        try:
            app = EventApplication.objects.get(id=app_id, event=event)
        except EventApplication.DoesNotExist:
            return Response({'error': 'Application not found.'}, status=status.HTTP_404_NOT_FOUND)
        app.status = 'rejected'
        app.save()
        send_user_notification(app.user, f"Your application for event '{event.name}' has been rejected.")
        return Response(EventApplicationSerializer(app).data)

    @action(detail=True, methods=['post'], url_path='applications/(?P<app_id>[^/.]+)/attend', permission_classes=[IsAdminUser])
    def mark_attendance(self, request, pk=None, app_id=None):
        event = self.get_object()
        try:
            app = EventApplication.objects.get(id=app_id, event=event)
        except EventApplication.DoesNotExist:
            return Response({'error': 'Application not found.'}, status=status.HTTP_404_NOT_FOUND)
        app.attended = True
        app.save()
        send_user_notification(app.user, f"You have been marked as attended for event '{event.name}'.")
        return Response(EventApplicationSerializer(app).data)

    @action(detail=True, methods=['post'], url_path='applications/(?P<app_id>[^/.]+)/reward', permission_classes=[IsAdminUser])
    def grant_reward(self, request, pk=None, app_id=None):
        event = self.get_object()
        try:
            app = EventApplication.objects.get(id=app_id, event=event)
        except EventApplication.DoesNotExist:
            return Response({'error': 'Application not found.'}, status=status.HTTP_404_NOT_FOUND)
        xp = request.data.get('reward_xp')
        currency = request.data.get('reward_currency')
        app.reward_xp = xp
        app.reward_currency = currency
        app.reward_granted = True
        app.save()
        send_user_notification(app.user, f"You have received a reward for attending event '{event.name}': XP={xp}, Currency={currency}")
        return Response(EventApplicationSerializer(app).data)

    @action(detail=True, methods=['post'], url_path='participants/(?P<user_id>[^/.]+)/approve', permission_classes=[IsAdminUser])
    def approve_participant(self, request, pk=None, user_id=None):
        event = self.get_object()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user not in event.attendees.all():
            return Response({'error': 'User is not a participant.'}, status=status.HTTP_400_BAD_REQUEST)
        # Mark as approved (could use a through model for more detail)
        # For now, just notify
        send_user_notification(user, f"Your participation in event '{event.name}' has been approved by an admin.")
        return Response({'status': 'participant approved'})

    @action(detail=True, methods=['post'], url_path='participants/(?P<user_id>[^/.]+)/reject', permission_classes=[IsAdminUser])
    def reject_participant(self, request, pk=None, user_id=None):
        event = self.get_object()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user not in event.attendees.all():
            return Response({'error': 'User is not a participant.'}, status=status.HTTP_400_BAD_REQUEST)
        event.attendees.remove(user)
        send_user_notification(user, f"Your participation in event '{event.name}' has been rejected by an admin.")
        return Response({'status': 'participant rejected'})

    @action(detail=False, methods=['get'])
    def past(self, request):
        now = timezone.now()
        past_events = Event.objects.filter(end_time__lt=now)
        serializer = self.get_serializer(past_events, many=True)
        return Response(serializer.data)

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.select_related('game', 'organizer', 'winner').prefetch_related('participants').all()
    serializer_class = TournamentSerializer
    filterset_class = TournamentFilter
    search_fields = ['name', 'description', 'status']

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        tournament = self.get_object()
        tournament.status = 'approved'
        tournament.save()
        send_user_notification(tournament.organizer, f"Your tournament, {tournament.name}, has been approved!")
        return Response({'status': 'tournament approved'})

    def perform_create(self, serializer):
        tournament = serializer.save(organizer=self.request.user)
        admins = User.objects.filter(is_admin=True)
        message = f"A new tournament, '{tournament.name}', has been created and is awaiting approval."
        send_group_notification(admins, message)

    def get_queryset(self):
        queryset = Tournament.objects.all()
        now = timezone.now().date()
        # Auto-update status based on time
        for tournament in queryset:
            if tournament.end_date and now > tournament.end_date and tournament.status != 'completed':
                tournament.status = 'completed'
                tournament.save(update_fields=['status'])
            elif tournament.start_date and now >= tournament.start_date and (not tournament.end_date or now <= tournament.end_date) and tournament.status != 'live':
                tournament.status = 'live'
                tournament.save(update_fields=['status'])
            elif tournament.start_date and now < tournament.start_date and tournament.status != 'upcoming':
                tournament.status = 'upcoming'
                tournament.save(update_fields=['status'])
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    @action(detail=True, methods=['get'])
    def bracket(self, request, pk=None):
        tournament = self.get_object()
        serializer = self.get_serializer(tournament)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        now = timezone.now()
        past_tournaments = Tournament.objects.filter(end_date__lt=now)
        serializer = self.get_serializer(past_tournaments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def pending_applications(self, request, pk=None):
        tournament = self.get_object()
        pending = tournament.participant_set.filter(is_approved=False)
        serializer = ParticipantSerializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='applications/(?P<participant_id>[^/.]+)/approve')
    def approve_application(self, request, pk=None, participant_id=None):
        try:
            participant = Participant.objects.get(id=participant_id, tournament_id=pk)
            participant.is_approved = True
            participant.save()

            team_leader = participant.team.created_by
            message = f"Your team, {participant.team.name}, has been approved to join the tournament: {participant.tournament.name}!"
            send_user_notification(team_leader, message)

            return Response({'status': 'approved'})
        except Participant.DoesNotExist:
            return Response({'error': 'Participant not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='applications/(?P<participant_id>[^/.]+)/reward')
    def grant_reward(self, request, pk=None, participant_id=None):
        from accounts.models import User
        from .models import TournamentAttendanceReward
        tournament = self.get_object()
        member_id = request.data.get('member_id')
        xp = request.data.get('reward_xp')
        currency = request.data.get('reward_currency')
        if not member_id:
            return Response({'error': 'member_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            participant = Participant.objects.get(id=participant_id, tournament_id=pk, is_approved=True)
        except Participant.DoesNotExist:
            return Response({'error': 'Approved team not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(id=member_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not participant.team.members.filter(id=user.id).exists():
            return Response({'error': 'User is not a member of this team.'}, status=status.HTTP_400_BAD_REQUEST)
        # Prevent duplicate rewards
        if TournamentAttendanceReward.objects.filter(tournament=tournament, user=user).exists():
            return Response({'error': 'Reward already granted to this user for this tournament.'}, status=status.HTTP_400_BAD_REQUEST)
        # Grant XP/currency (update user fields or use a service)
        if xp:
            user.xp = (user.xp or 0) + int(xp)
        if currency:
            user_currency = getattr(user, 'currency', 0)
            user.currency = user_currency + int(currency)
        user.save()
        TournamentAttendanceReward.objects.create(tournament=tournament, user=user, xp=xp, currency=currency)
        send_user_notification(user, f"You have received a reward for attending tournament '{tournament.name}': XP={xp}, Currency={currency}")
        return Response({'status': 'reward granted'})

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        from django.utils import timezone
        tournament = self.get_object()
        team_id = request.data.get('team_id')

        if not team_id:
            return Response({'error': 'team_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Only team leader can apply
        from teams.models import Team
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response({'error': 'Team not found.'}, status=status.HTTP_404_NOT_FOUND)
        if team.created_by != request.user:
            return Response({'error': 'Only the team leader can apply the team to the tournament.'}, status=status.HTTP_403_FORBIDDEN)

        # Check team size (must match the game for this tournament)
        required_size = getattr(tournament.game, 'team_size', None)
        if required_size is None:
            return Response({'error': 'This game does not have a team size set.'}, status=status.HTTP_400_BAD_REQUEST)
        if team.members.count() != required_size:
            return Response({'error': f'Team must have exactly {required_size} members to apply for this tournament.'}, status=status.HTTP_400_BAD_REQUEST)

        if tournament.apply_until and timezone.now() > tournament.apply_until:
            return Response({'error': 'Application deadline has passed.'}, status=status.HTTP_400_BAD_REQUEST)

        if Participant.objects.filter(tournament=tournament, team=team).exists():
            return Response({'error': 'This team has already applied to this tournament.'}, status=status.HTTP_400_BAD_REQUEST)

        Participant.objects.create(tournament=tournament, team=team)
        message = f'Your team, {team.name}, has successfully applied to the tournament: {tournament.name}'
        send_user_notification(request.user, message)

        return Response({'status': 'applied'})

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    http_method_names = ['patch']

    @action(detail=True, methods=['patch'], url_path='set_result')
    def set_result(self, request, pk=None):
        match = self.get_object()
        winner_id = request.data.get('winner_id')
        score = request.data.get('score')
        if not winner_id:
            return Response({'error': 'winner_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        match.winner_id = winner_id
        match.score = score
        match.is_completed = True
        match.save()
        # Check if this is the final match in the tournament
        tournament = match.round.tournament
        if not tournament.rounds.filter(matches__is_completed=False).exists():
            # All matches completed, set tournament winner
            tournament.winner_id = winner_id
            tournament.status = 'completed'
            tournament.save(update_fields=['winner_id', 'status'])

            # Grant rewards to the winning team
            winning_team = Team.objects.get(id=winner_id)
            primary_currency = Currency.objects.first()
            if primary_currency:
                for member in winning_team.members.all():
                    user_currency, created = UserCurrency.objects.get_or_create(
                        user=member,
                        currency=primary_currency
                    )
                    user_currency.balance += tournament.reward_currency
                    user_currency.save()
                    message = f"Your team, {winning_team.name}, has won the tournament '{tournament.name}' and you have been awarded {tournament.reward_currency} {primary_currency.name}!"
                    send_user_notification(member, message)

        return Response({'status': 'result set', 'winner_id': winner_id, 'score': score})
