from django.contrib import admin
from Admin_Panel.models import Table,Notification,FCMDevice



# Register your models here.


admin.site.register(Table)
admin.site.register(Notification)
admin.site.register(FCMDevice)

