from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import AchievementViewSet, UserAchievementViewSet

router = DefaultRouter()
router.register(r'achievements', AchievementViewSet)
router.register(r'user-achievements', UserAchievementViewSet, basename='userachievement')

urlpatterns = [
    path('', include(router.urls)),
]
