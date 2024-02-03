from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.

class MenuItems(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    availability = models.BooleanField(default=True)
    description = models.CharField(max_length=255,blank=True)
    image = models.ImageField(upload_to="Menu_Images/",blank=True,null=True)
    data_of_add = models.DateTimeField(auto_now_add=True)
    order_times = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Name:- {self.name} --- Price:- {self.price}"      


class YourOrderModel(models.Model):
    ORDER_STATUS = [
        ('Pending', 'Pending'),
        ('Complete', 'Complete'),
    ]
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
    order_number = models.CharField(max_length=100,blank=True)
    table_number = models.IntegerField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Pending')

    def __str__(self):
        return f"Order {self.order_id} ---Table Number:- {self.table_number} ---- Total Amount:- {self.total_amount} --- Order Status:- {self.order_status}"    
    
class OrderItem(models.Model):
    order = models.ForeignKey(YourOrderModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Order:- {self.order} ---- Name:- {self.name} --- Quantity:- {self.quantity} ---- Price:- {self.price}"
        
    
class CompletedOrder(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    PAYMENT_MODE = [
        ('Not Yet', 'Not Yet'),
        ('Cash', 'Cash'),
        ('Online', 'Online'),
    ]
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Done', 'Done'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    order_id = models.AutoField(primary_key=True)
    table_number = models.IntegerField(blank=True,null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE, default='Not Yet')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    overall_total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order ID: {self.order_id}--- Table Number:- {self.table_number} ----  Total Price: ₹{self.overall_total_price} --- Status:- {self.status} -- Payment Mode:-{self.payment_mode} --- Payment Status:- {self.payment_status}"

class CompleteOrderItem(models.Model):
    order = models.ForeignKey(CompletedOrder, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    menu = models.ForeignKey(MenuItems, on_delete=models.CASCADE,null=True,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order:- {self.order} ----- {self.quantity}x {self.name} - ₹{self.total_price}"


