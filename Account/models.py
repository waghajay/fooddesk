from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Admin_Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return f"User :- {self.user} ---- Is Admin:- {self.is_admin}"
    
