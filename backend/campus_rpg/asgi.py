"""
ASGI config for campus_rpg project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import teams.routing
import notifications.routing
import messaging.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_rpg.settings')

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            teams.routing.websocket_urlpatterns +
            notifications.routing.websocket_urlpatterns +
            messaging.routing.websocket_urlpatterns
        )
    ),
})
