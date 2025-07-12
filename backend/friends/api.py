from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Friendship
from .serializers import FriendshipSerializer
from django.contrib.auth import get_user_model

class FriendshipViewSet(viewsets.ModelViewSet):
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Allow access to all friendships involving the user, regardless of acceptance status
        return (Friendship.objects.filter(from_user=self.request.user) | Friendship.objects.filter(to_user=self.request.user)).order_by('id')

    @action(detail=False, methods=['get'])
    def requests(self, request):
        friend_requests = Friendship.objects.filter(to_user=request.user, is_accepted=False)
        serializer = self.get_serializer(friend_requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        friend_request.is_accepted = True
        friend_request.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        friend_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        to_user = get_user_model().objects.get(id=self.request.data['to_user'])
        serializer.save(from_user=self.request.user, to_user=to_user)
