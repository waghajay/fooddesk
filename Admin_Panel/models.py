# canteen/models.py
from django.db import models
import qrcode
import os
from django.conf import settings
import jwt
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class Table(models.Model):
    number = models.IntegerField(unique=True)
    qr_code_url = models.URLField(blank=True, null=True)
    qr_code_image = models.ImageField(upload_to='QR_codes/', blank=True, null=True)
    qr_data = models.CharField(max_length=255,blank=True,null=True)

    def generate_qr_code(self):
        # Embed data about the table in the QR code
        table_data = {
            'table_number': self.number,
        }

        # Encode the data into a JWT
        token = jwt.encode(table_data, settings.SECRET_KEY, algorithm='HS256')

        # Generate QR code with the encoded token
        external_url = f"https://www.fooddesk.store/menu/"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(external_url + f"?qr_data={token}")
        qr.make(fit=True)

        # Create a BytesIO buffer to save the image
        buffer = BytesIO()
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(buffer, format='PNG')

        # Save the QR code image in the model
        self.qr_code_image.save(f"{self.number}.png", ContentFile(buffer.getvalue()))
        self.qr_code_url = external_url + f"?qr_data={token}"
        self.qr_data = token

    def save(self, *args, **kwargs):
        # Check if the model is being saved for the first time or if some other condition applies
        if not self.qr_code_image:
            self.generate_qr_code()

        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Table Number :- {self.number}"
    
        

# 1. 👇 Add the following line
class Notification(models.Model):
    order_id = models.IntegerField()
    table_number = models.IntegerField()
    total_price = models.IntegerField()
    payment_mode = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20,blank=True,null=True)
    status = models.CharField(max_length=20,default="Pending")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order Id :- {self.order_id} -- Table Number:- {self.table_number} --- Price:- {self.total_price} -- Message :- {self.message}"
    

class FCMDevice(models.Model):
    registration_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.registration_id