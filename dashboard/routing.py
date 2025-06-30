# dashboard/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/realtime-data/$', consumers.RealtimeDataConsumer.as_asgi()),
]