from django.urls import path
from Admin_Panel.views import *
from Admin_Panel.views import *

urlpatterns = [
    
    path('noti', notificationpage, name='notification'),   
    # Admin Login
    
    path('login/',AdminLogin,name="AdminLogin"),
    path('logout/',AdminLogout,name="AdminLogout"),    
    
    path('',AdminIndex,name="AdminIndex"),
    path('menu/',AdminMenu,name="AdminMenu"),
    path("table/",AdminTable.as_view(),name="AdminTable"),
    path('order/',AdminOrder,name="AdminOrder"),    
    
    path('add_menu',AddMenuItem,name="AddMenuItem"),
    
    path('delete_table/', DeleteTableView.as_view(), name='delete_table'),
    path('delete_menu_item/', DeleteMenuItemView.as_view(), name='delete_menu_item'),
    
    path('notification/',AdminNotifaction,name="AdminNotifaction"),
    
    path("customer/",AdminCustomer,name="AdminCustomer"),
    path('delete_user/', delete_user, name='delete_user'),
    path("add_user/",AdminAddUser,name="AdminAddUser"),   
    
    path('update-order-status/', update_order_status, name='update_order_status'),
]
