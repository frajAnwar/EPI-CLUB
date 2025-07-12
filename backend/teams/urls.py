from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import TeamViewSet, TeamInvitationViewSet, ChangeTeamNameView

router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'invitations', TeamInvitationViewSet, basename='teaminvitation')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/teams/<int:team_id>/change-name/', ChangeTeamNameView.as_view(), name='change-team-name'),
]
