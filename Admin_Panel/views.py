from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from Menu.models import CompletedOrder,CompleteOrderItem,MenuItems
from django.db.models import Sum,Value,DecimalField
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from Admin_Panel.models import Table,Notification
from Account.models import Admin_Profile
from Admin_Panel.models import Table
from django.views import View
from Menu.models import MenuItems
from django.shortcuts import HttpResponse
from django.views.decorators.http import require_POST
import json
import requests

# Create your views here.


def notificationpage(request):
    return render(request, 'Admin_Panel/notification.html')


@login_required(login_url="AdminLogin")
def AdminIndex(request):    
    user_obj = User.objects.filter(username=request.user).first()        
    profile_obj = Admin_Profile.objects.filter(user=user_obj).first()        
    if profile_obj is None or not profile_obj.is_admin:
        messages.success(request, "You Don't Have The Permissin To Access The Dashboard \n Please Contact Admin")
        return redirect('AdminLogin')
    
    # Retriving the Counts of Staus
    total_order = CompletedOrder.objects.count()        
    total_pending = CompletedOrder.objects.filter(status='Pending').count()    
    total_Accepted = CompletedOrder.objects.filter(status='Accepted').count()    
    total_completed = CompletedOrder.objects.filter(status='Completed').count()
    total_cancelled = CompletedOrder.objects.filter(status='Cancelled').count()
    
    statuses = ['Pending', 'Accepted', 'Completed']

    # Create a dictionary to store total prices for each status
    total_prices = {}

    # Loop through each status and calculate the total price
    for status in statuses:
        total_prices[status] = CompletedOrder.objects.filter(status=status).aggregate(
            total_price=Coalesce(Sum('overall_total_price', output_field=DecimalField()), Value(0, output_field=DecimalField()))
        )['total_price']

    # Calculate the overall total price by summing up individual totals
    overall_total_price = sum(total_prices.values())
    
    # This Month and Last Month Order 
    this_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Get the first day of last month
    last_month_start = (this_month_start - timedelta(days=this_month_start.day)).replace(day=1)

    # Get the last day of last month
    last_month_end = this_month_start - timedelta(days=1)

    # Retrieve total orders for this month
    orders_this_month = CompletedOrder.objects.filter(
        created_at__gte=this_month_start,
        created_at__lte=datetime.now()
    ).count()

    # Retrieve total orders for last month
    orders_last_month = CompletedOrder.objects.filter(
        created_at__gte=last_month_start,
        created_at__lte=last_month_end
    ).count()    
    
    context = {
        "total_order":total_order,
        "total_pending":total_pending,
        "total_Accepted":total_Accepted,
        "total_completed":total_completed,
        "total_cancelled":total_cancelled,
        "overall_total_price":overall_total_price,
        'orders_this_month': orders_this_month,
        'orders_last_month': orders_last_month,
    }
    
    return render(request,"Admin_Panel/dashboard.html",context)


@login_required(login_url="AdminLogin")
def AdminMenu(request):    
    user_obj = User.objects.filter(username=request.user).first()        
    profile_obj = Admin_Profile.objects.filter(user=user_obj).first()        
    if profile_obj is None or not profile_obj.is_admin:
        messages.success(request, "You Don't Have The Permissin To Access The Dashboard \n Please Contact Admin")
        return redirect('AdminLogin')   
    
    menu_item = MenuItems.objects.all()
    context = {
        "menu_item":menu_item,
    }
    return render(request,"Admin_Panel/menu.html",context)


@login_required(login_url="AdminLogin")
def AdminOrder(request):    
    user_obj = User.objects.filter(username=request.user).first()        
    profile_obj = Admin_Profile.objects.filter(user=user_obj).first()        
    if profile_obj is None or not profile_obj.is_admin:
        messages.success(request, "You Don't Have The Permissin To Access The Dashboard \n Please Contact Admin")
        return redirect('AdminLogin')   
    
    orders = CompletedOrder.objects.all().order_by('-created_at')
    order_items = []
    
    for order in orders:
        item_for_order = CompleteOrderItem.objects.filter(order=order)
        order_items.extend(item_for_order)   
    
    context = {
        "orders":orders,
        "order_menu":order_items,
    }
    return render(request,"Admin_Panel/order.html",context)


@login_required(login_url="AdminLogin")
def AddMenuItem(request):    
    user_obj = User.objects.filter(username=request.user).first()        
    profile_obj = Admin_Profile.objects.filter(user=user_obj).first()        
    if profile_obj is None or not profile_obj.is_admin:
        messages.success(request, "You Don't Have The Permissin To Access The Dashboard \n Please Contact Admin")
        return redirect('AdminLogin')   

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        description = request.POST.get("description")
        image = request.FILES['image']
        
        menu = MenuItems.objects.create(
            name=name,
            price=price,
            availability=True,
            description=description,
            image=image,
        )
        menu.save()        
        return redirect("AdminMenu")    
    return HttpResponse("Add Item")


class DeleteMenuItemView(View):
    def post(self, request, *args, **kwargs):
        menu_item_id = request.POST.get('menu_item_id')

        if menu_item_id:
            try:
                menu_item = MenuItems.objects.get(id=int(menu_item_id))
                menu_item.delete()
                return JsonResponse({'success': True})
            except MenuItem.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Menu item not found'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid menu item id'})
        

class AdminTable(View):
    template_name = 'Admin_Panel/add_table.html'
    def get(self, request, *args, **kwargs):
        tables = Table.objects.all()
        return render(request, self.template_name, {"tables": tables})
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            table_number = request.POST.get('table_number')
            if table_number:
                table_number = int(table_number)
                print(f"Table Number Entered: {table_number}")

                # Check if a table with the same number already exists
                if not Table.objects.filter(number=table_number).exists():
                    # Create a new Table instance
                    table = Table(number=table_number)
                    table.save()
                    messages = ['Table created successfully.']

                    # Redirect to the same page to clear the form data
                    return redirect('AdminTable')

        # If the form submission fails or there's an error, render the template with existing tables and an error message
        tables = Table.objects.all()
        messages = ['Invalid request or table number already exists.']
        return render(request, self.template_name, {"tables": tables, 'messages': messages})   


class DeleteTableView(View):
    def post(self, request, *args, **kwargs):
        table_number = request.POST.get('table_number')

        if table_number:
            try:
                table = Table.objects.get(number=int(table_number))
                table.delete()
                return JsonResponse({'success': True})
            except Table.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Table not found'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid table number'})


@login_required(login_url="AdminLogin")    
def AdminNotifaction(request):
    user_obj = User.objects.filter(username=request.user).first()        
    profile_obj = Admin_Profile.objects.filter(user=user_obj).first()       
    if profile_obj is None or not profile_obj.is_admin:
        messages.success(request, "You Don't Have The Permissin To Access The Dashboard \n Please Contact Admin")
        return redirect('AdminLogin')
    
    notitication = Notification.objects.all().order_by('-created_at')
    return render(request,"Admin_Panel/admin_notification.html",{"notification":notitication})


@login_required(login_url="AdminLogin")
def AdminCustomer(request):
    user_obj = User.objects.filter(username=request.user).first()        
    profile_obj = Admin_Profile.objects.filter(user=user_obj).first()        
    if profile_obj is None or not profile_obj.is_admin:
        messages.success(request, "You Don't Have The Permissin To Access The Dashboard \n Please Contact Admin")
        return redirect('AdminLogin')
    
    users = User.objects.all()
    return render(request,"Admin_Panel/customer.html",{"users":users})


def AdminAddUser(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        if User.objects.filter(username=username).exists():         
            messages.success(request,"Usename already taken")
            return redirect('AdminCustomer')
        
        if User.objects.filter(email=email).exists():         
            messages.success(request,"Email already taken")
            return redirect('AdminCustomer')
 
        user = User.objects.create_user(username=username,password=password,email=email)
        user.save()
        admin_user = Admin_Profile.objects.create(user=user,is_admin=True)        

        messages.success(request,"User Created Successfully")
        return redirect("AdminCustomer")        
    return None
        

@csrf_exempt
def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id', None)
        if user_id:
            try:
                user_to_delete = User.objects.get(id=user_id)
                user_to_delete.delete()
                return HttpResponse('{"message": "User deleted successfully"}', content_type="application/json", status=200)
            except User.DoesNotExist:
                return HttpResponse('{"message": "User not found"}', content_type="application/json", status=404)

    return HttpResponse('{"message": "Invalid request"}', content_type="application/json", status=400)

@csrf_exempt
@login_required(login_url="AdminLogin")
@require_POST
def update_order_status(request):
    user_obj = User.objects.filter(username=request.user).first()        
    profile_obj = Admin_Profile.objects.filter(user=user_obj).first()        
    if profile_obj is None or not profile_obj.is_admin:
        messages.success(request, "You Don't Have The Permissin To Access The Dashboard \n Please Contact Admin")
        return redirect('AdminLogin')
        
    try:
        data = json.loads(request.body)
        order_id = data.get('orderId')
        current_status = data.get('currentStatus')
        new_status = data.get('newStatus')
        
        order = CompletedOrder.objects.get(order_id=order_id)
        
        order.status = new_status
        order.save()

        return JsonResponse({'status': 'success', 'message': 'Order status changed successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def AdminLogin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user_obj = User.objects.filter(username=username).first()
        
        if user_obj is None:
            messages.success(request, "User Not Found")
            return redirect('AdminLogin')
        
        profile_obj = Admin_Profile.objects.filter(user=user_obj).first()
        
        if profile_obj is None or not profile_obj.is_admin:
            messages.success(request, "You Are not an Admin")
            return redirect('AdminLogin')
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            messages.success(request, "Wrong Password")
            return redirect('AdminLogin')
        
        login(request, user)
        
        next_url = request.GET.get('next')
        
        if next_url:
            return redirect(next_url)
        else:
            return redirect('AdminIndex')
        
    return render(request, "Account/dashboard/login.html")

def AdminLogout(request):
    logout(request)
    return redirect("AdminLogin")



def send_notification(registration_ids, message_title, message_desc):
    fcm_api_key = 'AAAAvFYj7Ac:APA91bF2NxwQ63-Thmxee6W9TMzzeFgthXL_rZj5tbhBMUNTbEMl6b9kst-Be_JY-nJCMZTYMlPxSTljCqEIetucHJ3DUjcUcko83TU_weXAHthf8w24t3yMXmZanTjRsrSZAKaqrXNk'
    url = 'https://fcm.googleapis.com/fcm/send'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + fcm_api_key,
    }

    payload = {
        'registration_ids': registration_ids,
        'priority': 'high',
        'notification': {   
            'body': message_desc,
            'title': message_title,
        },
        'data': {
            'click_action': 'https://fooddesk.onrender.com/dash/order/',
        }
    }

    result = requests.post(url, data=json.dumps(payload), headers=headers)
    return result.json()




from Admin_Panel.models import FCMDevice

@csrf_exempt
def store_fcm_token(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        print("Token :--- ", token)
        # Store the token in your database (modify this according to your model)
        # Example assuming you have a model named FCMToken:
        FCMDevice.objects.create(registration_id=token)
        print("Saved")
        return JsonResponse({'status': 'Token stored successfully'})
    else:
        print("NOt Saved")
        return JsonResponse({'status': 'Invalid request method'})
    
    
def send_push(request):
    # Assuming FCMToken model has a field 'token' to store FCM tokens
    registration_ids = FCMDevice.objects.values_list('registration_id', flat=True)
    
    # Convert the QuerySet to a list
    registration_ids = list(registration_ids)

    if registration_ids:
        result = send_notification(registration_ids, 'New Order Received', 'Order Alert,,Order Alert............')
        return HttpResponse(json.dumps(result), content_type='application/json')
    else:
        return HttpResponse('No FCM tokens found in the database', status=400)