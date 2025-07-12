from django.urls import path
from .api import FriendshipViewSet

app_name = "friends"

urlpatterns = [
    path('friendships/', FriendshipViewSet.as_view({'get': 'list', 'post': 'create'}), name='friendship-list'),
    path('friendships/requests/', FriendshipViewSet.as_view({'get': 'requests'}), name='friendship-requests'),
    path('friendships/<int:pk>/', FriendshipViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='friendship-detail'),
    path('friendships/<int:pk>/accept/', FriendshipViewSet.as_view({'post': 'accept'}), name='friendship-accept'),
    path('friendships/<int:pk>/decline/', FriendshipViewSet.as_view({'post': 'decline'}), name='friendship-decline'),
]
