from django.shortcuts import render,redirect,get_object_or_404,reverse
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from Menu.models import MenuItems
from django.views.decorators.http import require_POST
from django.db import transaction
import json
from .models import YourOrderModel, OrderItem,CompletedOrder, CompleteOrderItem
from Admin_Panel.models import Notification,Table
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your views here.

def index(request):
    items = MenuItems.objects.all()
    return render(request,"Menu/index.html",{"items":items})

def ProductDetails(request,id):
    item = MenuItems.objects.get(id=id)
    print(item.image)
    return render(request,"Menu/product_details.html",{"items":item})


User = get_user_model()

@csrf_exempt
@require_POST
def process_order(request):
    try:
        order_data = json.loads(request.body) 
        
        with transaction.atomic():
            if request.user.is_authenticated:
                order_instance = YourOrderModel.objects.create(user=request.user, order_status="Pending")
            else:
                order_instance = YourOrderModel.objects.create(order_status="Pending")
            
            for item_data in order_data:
                OrderItem.objects.create(
                    order=order_instance,
                    name=item_data.get('name', ''),
                    quantity=item_data.get('quantity', 0),
                    price=item_data.get('price', 0)
                )
                
            table_number = item_data.get('tablenumber',0)
            
                
            order_instance.order_number = order_instance.id
            order_instance.table_number = table_number
            order_instance.save()
            
        request.session['order_id'] = str(order_instance.order_id)

        response_data = {
            'message': 'Order processed successfully',
            'order_id': str(order_instance.order_id),
            'sessionid': request.session.session_key,
        }
        return JsonResponse(response_data)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    

def checkout(request):
    order_id = request.session.get('order_id')
    if order_id:
        order_instance = get_object_or_404(YourOrderModel, order_id=order_id)
        if order_instance.order_status == "Complete":
            return render(request,'Menu/checkout.html',{"message" : "Order has benn already placed please see the Order History Page"})
        table_number = order_instance.table_number
        order_items = order_instance.orderitem_set.all()

        return render(request, 'Menu/checkout.html', {
            'order_instance': order_instance,
            'order_items': order_items,
            'table_number':table_number,
        })
    else:
        return JsonResponse({'error': 'Order ID not found in the session'}, status=400)
    
    
def checkouterror(request):
    return render(request,'Menu/checkout_error.html')


from Admin_Panel.models import FCMDevice
from Admin_Panel.views import send_notification

@csrf_exempt
def complete_order(request):
    if request.method == 'POST':      
        try:
            data = json.loads(request.body)
            order_items = data.get('order_items', [])
            overall_total_price = data.get('overall_total_price', 0)
            payment_method = data.get('payment_method', '')            
            
            table_number = data.get('table_number',0)
            
            s_id = request.session.get('order_id')
            yourordermodel_status_check = YourOrderModel.objects.get(order_id=s_id)

            if yourordermodel_status_check.order_status == "Complete":
                return JsonResponse({'message': 'Order completed Order Already Completed', 'redirect_url': '/checkout_error'})
        
            if payment_method == "cash":
                if request.user.is_authenticated:
                    order = CompletedOrder.objects.create(overall_total_price=overall_total_price, user=request.user,payment_mode="Cash",table_number=table_number)
                else:
                    order = CompletedOrder.objects.create(overall_total_price=overall_total_price,payment_mode="Cash",table_number=table_number)           

                for item in order_items:
                    CompleteOrderItem.objects.create(
                        order=order,
                        name=item['name'],
                        quantity=item['quantity'],
                        price=item['price'],
                        total_price=item['total_price']
                    )
                    
                registration_ids = FCMDevice.objects.values_list('registration_id', flat=True)
                
                # Convert the QuerySet to a list
                registration_ids = list(registration_ids)

                if registration_ids:
                    result = send_notification(registration_ids, 'New Order', f'New Order....\n Order Id :- {order.order_id}, Table Number :- {table_number}, Total Price :- {overall_total_price}, Payment Mode:- Cash, Payment Status :- Pending')
                
                notify = Notification.objects.create(order_id=order.order_id,table_number=table_number,total_price=overall_total_price,payment_mode="Cash",payment_status="Pending",status="Pending",message=f"New Order....\n Order Id :- {order.order_id}, Table Number :- {table_number}, Total Price :- {overall_total_price}, Payment Mode:- Cash, Payment Status :- Pending")
                notify.save()
                
                s_id = request.session.get('order_id')

                
                yourordermodel_status_update = YourOrderModel.objects.get(order_id=s_id)
                yourordermodel_status_update.order_status = "Complete"
                yourordermodel_status_update.save()
                

                
                request.session['order_id'] = str(order.order_id)
                return JsonResponse({'message': 'Order completed successfully With Cash Mode', 'order_id': order.order_id, 'redirect_url': reverse('order_history'),'sessionid': request.session.session_key,})
            
            if payment_method == "online":
                
                if request.user.is_authenticated:
                    order = CompletedOrder.objects.create(overall_total_price=overall_total_price, user=request.user,payment_mode="Online",payment_status="Done",table_number=table_number) 
                else:
                    order = CompletedOrder.objects.create(overall_total_price=overall_total_price,payment_mode="Online",payment_status="Done",table_number=table_number) 
                          

                for item in order_items:
                    CompleteOrderItem.objects.create(
                        order=order,
                        name=item['name'],
                        quantity=item['quantity'],
                        price=item['price'],
                        total_price=item['total_price']
                    )
                    
                if registration_ids:
                    result = send_notification(registration_ids, 'Ajay Wagh', 'Mobile Alert')
                    
                notify = Notification.objects.create(order_id=order.order_id,table_number=table_number,total_price=overall_total_price,payment_mode="Online",status="Pending",payment_status="Done",message=f"New Order....\n Order Id :- {order.order_id}, Table Number :- {table_number}, Total Price :- {overall_total_price}, Payment Mode:- Online, Payment Status :- Done")
                notify.save()
                
                return JsonResponse({'message': 'Order completed successfully With Online Mode', 'order_id': order.order_id, 'redirect_url': reverse('notification')})
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def OrderHistory(request):
    log_in = request.user
    if request.user.is_authenticated:
        orders = CompletedOrder.objects.filter(user=log_in).order_by('-created_at')
        order_items = []
        
        for order in orders:
            items_for_order = CompleteOrderItem.objects.filter(order=order)
            order_items.extend(items_for_order)
            
        return render(request, "Menu/order_history.html", {"orders": orders, "order_menu": order_items})
    else:
        order_id = request.session.get('order_id')
        if order_id:
            orders = CompletedOrder.objects.filter(order_id=order_id).order_by('-created_at')
            order_items = []
            
            for order in orders:
                items_for_order = CompleteOrderItem.objects.filter(order=order)
                order_items.extend(items_for_order)
            
        return render(request, "Menu/order_history.html",{"message":f"You have not logged in Please Login first","orders": orders, "order_menu": order_items})


@csrf_exempt
@require_POST
def cancel_order(request):
    try:
        order_id = request.POST.get('order_id')
        order = CompletedOrder.objects.get(order_id=order_id)
        order.status = 'Cancelled'
        order.save()

        return JsonResponse({'status': 'success', 'message': 'Order cancelled successfully'})
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Order not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def show_menu_external(request):
    qr_data = request.GET.get('qr_data')
    try:    
        # Decode the JWT
        table_data = jwt.decode(qr_data, settings.SECRET_KEY, algorithms=['HS256'])
        table_number = table_data['table_number']

        all_menu_items = MenuItems.objects.all()

        return render(request,"Menu/QRcode.html" , {"menu_items":all_menu_items,"table_number":table_number})
    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'Token has expired'}, status=400)
    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Invalid token'}, status=400)



def TestQR(request):
    return render(request,"Menu/testQR.html")




def showFirebaseJS(request):
    data = 'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");' \
           'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js"); ' \
           'var firebaseConfig = {' \
           '        apiKey: "AIzaSyCecVymwb21GQM2YtueZEU-J6P8baVoYSs",' \
           '        authDomain: "django-notify-24593.firebaseapp.com",' \
           '        databaseURL: "https://django-notify-24593-default-rtdb.asia-southeast1.firebasedatabase.app",' \
           '        projectId: "django-notify-24593",' \
           '        storageBucket: "django-notify-24593.appspot.com",' \
           '        messagingSenderId: "808899046407",' \
           '        appId: "1:808899046407:web:cacddfc6db8310e3e9cea2",' \
           ' };' \
           'firebase.initializeApp(firebaseConfig);' \
           'const messaging=firebase.messaging();' \
           'messaging.setBackgroundMessageHandler(function (payload) {' \
           '    console.log(payload);' \
           '    const notification=JSON.parse(payload);' \
           '    const notificationOption={' \
           '        body:notification.body,' \
           '        icon:notification.icon' \
           '    };' \
           '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
           '});'

    return HttpResponse(data, content_type="text/javascript")

from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from .models import CompletedOrder
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

class DownloadInvoiceView(View):
    def get(self, request, order_id):
        # Get the order object
        order = CompletedOrder.objects.get(order_id=order_id)
        order_items = CompleteOrderItem.objects.filter(order=order)
        
        

        # Render HTML template with dynamic data
        html_content = render_to_string('Menu/invoice_template.html', {'order': order,"order_items":order_items})

        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'

        # Generate PDF
        pisa.CreatePDF(html_content, dest=response)

        return response


