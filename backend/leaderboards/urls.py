from django.urls import path
from .api import LeaderboardView

urlpatterns = [
    path('', LeaderboardView.as_view(), name='leaderboards'),
]
