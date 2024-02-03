from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'public_room',
            {
                "type": "send_notification",
                "order_id": instance.order_id,
                "table_number": instance.table_number,
                "total_price": instance.total_price,
                "payment_mode": instance.payment_mode,
                "payment_status": instance.payment_status,
                "status": instance.status,
                "message": instance.message,
            }
        )