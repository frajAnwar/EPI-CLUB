
import django_filters
from .models import Event, Tournament

class EventFilter(django_filters.FilterSet):
    class Meta:
        model = Event
        fields = {
            'start_time': ['gte', 'lte'],
            'status': ['exact'],
        }

class TournamentFilter(django_filters.FilterSet):
    class Meta:
        model = Tournament
        fields = {
            'start_date': ['gte', 'lte'],
            'status': ['exact'],
            'game': ['exact'],
        }
