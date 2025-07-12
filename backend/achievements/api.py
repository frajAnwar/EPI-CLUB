from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Achievement, UserAchievement
from .serializers import AchievementSerializer, UserAchievementSerializer

class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all().order_by('id')
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user).order_by('id')

    @action(detail=True, methods=['post'])
    def toggle_display(self, request, pk=None):
        user_achievement = self.get_object()
        if user_achievement.user != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user_achievement.displayed = not user_achievement.displayed
        user_achievement.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
