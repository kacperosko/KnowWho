from django.urls import path, include
from apps.game.consumers import ChatConsumer

# Here, "" is routing to the URL ChatConsumer which
# will handle the chat functionality.
websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', ChatConsumer.as_asgi()),
    path('', ChatConsumer.as_asgi()),
]
