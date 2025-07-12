from rest_framework import viewsets, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .models import User, Game, ActivityLog
from .serializers import (
    UserAdminSerializer, GameSerializer, ActivityLogSerializer, 
    UserProfileSerializer, UserApprovalSerializer, ChangeUsernameSerializer, BanUserSerializer, SetUsernameSerializer
)
from items.models import Item, InventoryItem
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.contrib.auth import login, authenticate


class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_approved:
                login(request, user)
                serializer = UserProfileSerializer(user)
                return Response({"user": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Account not approved."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({'detail': 'CSRF cookie set'})

class UserApprovalViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_approved=False)
    serializer_class = UserApprovalSerializer
    http_method_names = ['get', 'patch']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = self.get_object()
        user.is_approved = True
        user.save()
        send_user_notification(user, "Your account has been approved!")
        return Response({'status': 'user approved'})

class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]

class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all().order_by('id')
    serializer_class = GameSerializer

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserProfileSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ChangeUsernameView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangeUsernameSerializer(data=request.data)
        if serializer.is_valid():
            new_username = serializer.validated_data['username']
            user = request.user
            try:
                item_to_use = InventoryItem.objects.get(user=user, item__name="Username Change")
                
                if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                    return Response({'error': 'This username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

                user.username = new_username
                user.save()
                item_to_use.delete()
                ActivityLog.objects.create(user=user, action="Username Changed", details={'new_username': new_username})

                return Response({'status': 'Username changed successfully!'})

            except InventoryItem.DoesNotExist:
                return Response({'error': 'You do not have the required item to change your username.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetUsernameView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.username:  # Already set
            return Response({'error': 'Username already set.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = SetUsernameSerializer(data=request.data)
        if serializer.is_valid():
            user.username = serializer.validated_data['username']
            user.save()
            return Response({'status': 'Username set successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LevelRankConfigView(views.APIView):
    def get(self, request, *args, **kwargs):
        config = {
            'ranks': {
                'E': {'min_level': 1, 'max_level': 9},
                'D': {'min_level': 10, 'max_level': 19},
                'C': {'min_level': 20, 'max_level': 29},
                'B': {'min_level': 30, 'max_level': 39},
                'A': {'min_level': 40, 'max_level': 49},
                'S': {'min_level': 50, 'max_level': 59},
            },
            'level_xp_requirements': {}
        }
        return Response(config)

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all().order_by('-timestamp')
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdminUser]

class BanUserView(views.APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id, *args, **kwargs):
        serializer = BanUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user_to_ban = User.objects.get(id=user_id)
                is_banned = serializer.validated_data['is_banned']

                if user_to_ban.is_admin:
                    return Response({'error': 'Admins cannot be banned.'}, status=status.HTTP_403_FORBIDDEN)

                user_to_ban.is_banned = is_banned
                user_to_ban.is_active = not is_banned
                user_to_ban.save()

                action_text = "User Banned" if is_banned else "User Unbanned"
                ActivityLog.objects.create(user=request.user, action=action_text, details={'target_user_id': user_to_ban.id})

                return Response({'status': f'User has been {action_text.lower()}.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
