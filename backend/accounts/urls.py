from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    UserProfileViewSet, UserApprovalViewSet, GameViewSet, UserAdminViewSet, 
    ActivityLogViewSet, BanUserView, LevelRankConfigView, LoginView, SetUsernameView
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'admin/approvals', UserApprovalViewSet, basename='user-approval')
router.register(r'admin/users', UserAdminViewSet, basename='user-admin')
router.register(r'admin/activity-log', ActivityLogViewSet, basename='activity-log')
router.register(r'games', GameViewSet)

from .views import registration_view, admin_approval_queue, approve_user, reject_user, analytics_view

urlpatterns = [
    path('login/', LoginView.as_view(), name='api-login'),
    path('', include(router.urls)),
    path('api/admin/users/<int:user_id>/ban/', BanUserView.as_view(), name='ban-user'),
    path('api/level-rank-config/', LevelRankConfigView.as_view(), name='level-rank-config'),
    path('register/', registration_view, name='register'),
    path('set-username/', SetUsernameView.as_view(), name='set-username'),
    path('admin/approval', admin_approval_queue, name='admin_approval_queue'),
    path('admin/approve/<int:user_id>/', approve_user, name='approve_user'),
    path('admin/reject/<int:user_id>/', reject_user, name='reject_user'),
    path('api/analytics/', analytics_view, name='analytics'),
]
