# dashboard/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RealtimeDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'realtime_data_group'

        # Join the group.
        # The channel_layer will use Redis to manage this group across all servers.
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # This method is called when a message is sent to the group from the backend.
    # The name 'broadcast_data' is a custom name we define.
    async def broadcast_data(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))