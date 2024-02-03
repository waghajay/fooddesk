import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'public_room'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({ 
                                                'message': event['message'],
                                                'order_id': event['order_id'],
                                                'table_number': event['table_number'],
                                                'total_price': event['total_price'],
                                                'payment_mode': event['payment_mode'],
                                                'payment_status': event['payment_status'],
                                                'status': event['status']
                                            }))