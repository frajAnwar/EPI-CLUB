import django_filters
from .models import ProfileBanner

class ProfileBannerFilter(django_filters.FilterSet):
    class Meta:
        model = ProfileBanner
        fields = {
            'name': ['icontains'],
            'cost': ['gte', 'lte'],
            'is_unlockable': ['exact'],
        }
