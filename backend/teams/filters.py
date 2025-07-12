import django_filters
from .models import Team
from django.db import models

class TeamFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    tag = django_filters.CharFilter(lookup_expr='icontains')
    game = django_filters.NumberFilter(field_name='game__id')
    min_members = django_filters.NumberFilter(method='filter_min_members')
    max_members = django_filters.NumberFilter(method='filter_max_members')

    class Meta:
        model = Team
        fields = ['name', 'tag', 'game']

    def filter_min_members(self, queryset, name, value):
        return queryset.annotate(num_members=models.Count('members')).filter(num_members__gte=value)

    def filter_max_members(self, queryset, name, value):
        return queryset.annotate(num_members=models.Count('members')).filter(num_members__lte=value)
