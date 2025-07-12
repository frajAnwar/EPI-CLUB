from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from accounts.models import User
from teams.models import Team
from events.models import Event, Tournament
from items.models import Item

class DashboardAnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        from django.utils import timezone
        from datetime import timedelta
        from items.models import InventoryItem
        from accounts.models import ActivityLog

        now = timezone.now()
        total_users = User.objects.count()
        total_teams = Team.objects.count()
        total_events = Event.objects.count()
        total_tournaments = Tournament.objects.count()
        total_items = Item.objects.count()
        active_users_24h = User.objects.filter(last_login__gte=now - timedelta(hours=24)).count()
        new_users_7d = User.objects.filter(date_joined__gte=now - timedelta(days=7)).count()
        most_active_teams = list(Team.objects.annotate(member_count=models.Count('members')).order_by('-member_count')[:5].values('name', 'member_count'))
        most_popular_events = list(Event.objects.annotate(attendee_count=models.Count('attendees')).order_by('-attendee_count')[:5].values('name', 'attendee_count'))
        top_items = list(InventoryItem.objects.values('item__name').annotate(total=models.Sum('quantity')).order_by('-total')[:5])
        recent_activity = list(ActivityLog.objects.order_by('-timestamp').values('user__username', 'action', 'timestamp')[:10])

        return Response({
            'total_users': total_users,
            'active_users_24h': active_users_24h,
            'new_users_7d': new_users_7d,
            'total_teams': total_teams,
            'most_active_teams': most_active_teams,
            'total_events': total_events,
            'most_popular_events': most_popular_events,
            'total_tournaments': total_tournaments,
            'total_items': total_items,
            'top_items': top_items,
            'recent_activity': recent_activity,
        })
