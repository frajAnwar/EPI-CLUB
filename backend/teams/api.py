from rest_framework import viewsets, permissions, serializers, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Team, ChatMessage, TeamInvitation
from .serializers import TeamSerializer, TeamMemberSerializer
from .serializers import TeamSerializer, TeamMemberSerializer, ChangeTeamNameSerializer
from notifications.utils import send_user_notification
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from items.models import InventoryItem
from accounts.models import ActivityLog, User
from .utils import get_suggested_teams
from .filters import TeamFilter
from django_filters.rest_framework import DjangoFilterBackend

class ChatMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = ChatMessage
        fields = ('id', 'username', 'message', 'timestamp')

class IsTeamMember(permissions.BasePermission):
    """
    Allows access only to team members.
    """
    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id).exists()

class IsTeamLeader(permissions.BasePermission):
    """
    Allows access only to the team leader (creator).
    """
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as an admin user, or is a read-only request.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.select_related('game', 'created_by').prefetch_related('members').all()
    serializer_class = TeamSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TeamFilter
    search_fields = ['name', 'tag', 'created_by__username']
    filterset_fields = ['game', 'created_by', 'is_active']

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        team = self.get_object()
        team.is_active = True
        team.save()
        send_user_notification(team.created_by, f"Your team, {team.name}, has been approved!")
        return Response({'status': 'team approved'})

    @action(detail=False, methods=['get'])
    def suggested(self, request):
        teams = get_suggested_teams(request.user)
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'manage_members']:
            self.permission_classes = [permissions.IsAuthenticated, IsTeamLeader]
        elif self.action == 'chat_history':
            self.permission_classes = [permissions.IsAuthenticated, IsTeamMember]
        elif self.action in ['list', 'retrieve', 'suggested']:
            self.permission_classes = [permissions.IsAuthenticated | IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        game = serializer.validated_data['game']
        user = self.request.user
        if Team.objects.filter(members=user, game=game).exists():
            raise ValidationError('You are already on a team for this game.')
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post', 'delete'], url_path='members')
    def manage_members(self, request, pk=None):
        team = self.get_object()
        serializer = TeamMemberSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)

            if request.method == 'POST':
                if team.members.count() >= team.game.team_size:
                    return Response({'error': f'Team is full. Maximum size is {team.game.team_size} members.'}, status=400)
                team.members.add(user)
                send_user_notification(user, f"You have been added to the team: {team.name}")
                return Response({'status': 'member added'})

            elif request.method == 'DELETE':
                team.members.remove(user)
                send_user_notification(user, f"You have been removed from the team: {team.name}")
                return Response({'status': 'member removed'})
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'])
    def chat_history(self, request, pk=None):
        team = self.get_object()
        messages = team.chat_messages.order_by('timestamp').all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

class ChangeTeamNameView(views.APIView):
    permission_classes = [IsAuthenticated, IsTeamLeader]

    def post(self, request, team_id, *args, **kwargs):
        serializer = ChangeTeamNameSerializer(data=request.data)
        if serializer.is_valid():
            new_name = serializer.validated_data['name']
            new_tag = serializer.validated_data['tag']
            user = request.user
            try:
                team = Team.objects.get(id=team_id, created_by=user)
                item_to_use = InventoryItem.objects.get(user=user, item__name="Team Name Change")

                if Team.objects.filter(name=new_name).exclude(pk=team.pk).exists() or \
                   Team.objects.filter(tag=new_tag).exclude(pk=team.pk).exists():
                    return Response({'error': 'This name or tag is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

                team.name = new_name
                team.tag = new_tag
                team.save()
                item_to_use.delete()
                ActivityLog.objects.create(user=user, action="Team Name Changed", details={'team_id': team.id, 'new_name': new_name, 'new_tag': new_tag})

                return Response({'status': 'Team name and tag changed successfully!'})

            except InventoryItem.DoesNotExist:
                return Response({'error': 'You do not have the required item.'}, status=status.HTTP_400_BAD_REQUEST)
            except Team.DoesNotExist:
                return Response({'error': 'Team not found or you are not the leader.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeamInvitationSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    class Meta:
        model = TeamInvitation
        fields = ('id', 'team', 'team_name', 'invited_user')

class TeamInvitationViewSet(viewsets.ModelViewSet):
    serializer_class = TeamInvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return self.request.user.team_invitations.all()

    def perform_create(self, serializer):
        team = serializer.validated_data['team']
        if team.created_by != self.request.user:
            raise ValidationError("You are not the leader of this team.")
        instance = serializer.save()
        send_user_notification(instance.invited_user, f"You have been invited to join {team.name}!")

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        invitation = self.get_object()
        team = invitation.team
        user = request.user

        if team.members.count() >= team.game.team_size:
            return Response({'error': 'This team is now full.'}, status=status.HTTP_400_BAD_REQUEST)

        team.members.add(user)
        send_user_notification(team.created_by, f"{user.username} has accepted your invitation to join {team.name}.")
        invitation.delete()
        return Response({'status': 'Invitation accepted.'})

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        invitation = self.get_object()
        send_user_notification(invitation.team.created_by, f"{request.user.username} has declined your invitation.")
        invitation.delete()
        return Response({'status': 'Invitation declined.'})
