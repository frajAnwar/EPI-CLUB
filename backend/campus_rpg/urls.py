"""
URL configuration for campus_rpg project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from accounts.views import custom_login_view, home_view, profile_edit_view, profile_view, discord_link, discord_callback
from accounts.api import GetCSRFToken
from accounts.admin_economy_dashboard import economy_dashboard

urlpatterns = [
    path('api/csrf/', GetCSRFToken.as_view(), name='get-csrf-token'),
    path('', home_view, name='home'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('admin/', admin.site.urls),
    path('economy-dashboard/', economy_dashboard, name='economy-dashboard'),
    path('accounts/profile/', profile_view, name='profile'),
    path('accounts/', include('allauth.urls')),
    path('accounts/discord/link/', discord_link, name='discord_link'),
    path('accounts/discord/callback/', discord_callback, name='discord_callback'),
    path('api/v1/', include([
        path('accounts/', include('accounts.urls')),
        path('events/', include('events.urls')),
        path('dungeons/', include('dungeons.urls')),
        path('trading/', include('trading.urls')),
        path('quests/', include('quests.urls')),
        path('news/', include('news.urls')),
        path('teams/', include('teams.urls')),
        path('notifications/', include('notifications.urls')),
        path('achievements/', include('achievements.urls')),
        path('search/', include('search.urls')),
        path('analytics/', include('analytics.urls')),
        path('admin/', include('roles.urls')),
        path('leaderboards/', include('leaderboards.urls')),
        path('cosmetics/', include('cosmetics.urls')),
        path('friends/', include('friends.urls')),
        path('messaging/', include('messaging.urls')),
        path('forum/', include('forum.urls')),
    ])),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
