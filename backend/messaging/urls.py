from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ConversationViewSet, DirectMessageViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', DirectMessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]
