from django.urls import path
from Menu.views import *

urlpatterns = [
    path("",index,name="index"),
    path("product/<int:id>",ProductDetails,name="product"),
    path('process_order/', process_order, name='process_order'),
    path('checkout/', checkout, name='checkout'),
    path('checkout_error/', checkouterror, name='checkout_error'),
    path('complete_order/', complete_order, name='complete_order'),
    path('order_history/', OrderHistory, name='order_history'),
    path('cancel_order/', cancel_order, name='cancel_order'),
    
    path('menu/', show_menu_external, name='show_menu_external'),
    
    path("test/",TestQR,name="Test"),
    
    path('firebase-messaging-sw.js',showFirebaseJS,name="show_firebase_js"),
    
    path('download_invoice/<int:order_id>/', DownloadInvoiceView.as_view(), name='download_invoice'),




]