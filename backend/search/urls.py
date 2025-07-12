from django.urls import path
from .api import GlobalSearchView

urlpatterns = [
    path('', GlobalSearchView.as_view(), name='global-search'),
]
