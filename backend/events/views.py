from rest_framework import viewsets
from .models import Event, Tournament
from .serializers import EventSerializer, TournamentSerializer
from news.models import News
from news.serializers import NewsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

class CalendarView(APIView):
    def get(self, request, *args, **kwargs):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({"error": "Date parameter is required"}, status=400)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        events = Event.objects.filter(start_time__date=date)
        tournaments = Tournament.objects.filter(start_date=date)
        news = News.objects.filter(created_at__date=date)

        event_serializer = EventSerializer(events, many=True)
        tournament_serializer = TournamentSerializer(tournaments, many=True)
        news_serializer = NewsSerializer(news, many=True)

        return Response({
            'events': event_serializer.data,
            'tournaments': tournament_serializer.data,
            'news': news_serializer.data
        })
