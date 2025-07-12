from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import QuestViewSet, UserQuestViewSet

router = DefaultRouter()
router.register(r'quests', QuestViewSet)
router.register(r'user-quests', UserQuestViewSet, basename='userquest')

urlpatterns = router.urls
