from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import NewsViewSet

router = DefaultRouter()
router.register(r'news', NewsViewSet)

urlpatterns = router.urls
