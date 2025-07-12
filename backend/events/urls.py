from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import EventViewSet, TournamentViewSet, MatchViewSet
from .views import CalendarView

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'tournaments', TournamentViewSet)
router.register(r'matches', MatchViewSet)

urlpatterns = router.urls + [
    path('calendar/', CalendarView.as_view(), name='calendar'),
]
