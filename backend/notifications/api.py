from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('id')
    serializer_class = NotificationSerializer

    def get_queryset(self):
        queryset = self.request.user.notifications.all()
        read_param = self.request.query_params.get('read')
        if read_param is not None:
            if read_param.lower() == 'true':
                queryset = queryset.filter(read=True)
            elif read_param.lower() == 'false':
                queryset = queryset.filter(read=False)
        return queryset

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @action(detail=True, methods=['post'])
    def mark_as_unread(self, request, pk=None):
        notification = self.get_object()
        notification.read = False
        notification.save()
        return Response({'status': 'notification marked as unread'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(read=True)
        return Response({'status': 'all notifications marked as read'})
