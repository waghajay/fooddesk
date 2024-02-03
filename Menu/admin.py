from django.contrib import admin
from Menu.models import *


# Register your models here.

admin.site.register(YourOrderModel)
admin.site.register(OrderItem)
admin.site.register(MenuItems)
admin.site.register(CompletedOrder)
admin.site.register(CompleteOrderItem)

