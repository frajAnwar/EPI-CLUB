from rest_framework import viewsets
from .models import News
from .serializers import NewsSerializer

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by('id')
    serializer_class = NewsSerializer
    search_fields = ['title', 'content', 'author__username']
    filterset_fields = ['published', 'created_at', 'author']
