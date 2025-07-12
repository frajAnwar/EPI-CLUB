from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ProfileBannerViewSet

router = DefaultRouter()
router.register(r'banners', ProfileBannerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
