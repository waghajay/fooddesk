from django.urls import path
from Account.views import *


urlpatterns = [
    path('',UserLogin,name="login"),
    path('register/',UserRegister,name="register"),
    path('logout/',UserLogout,name="logout"),
    
    # path("setting/",UserSetting,name="setting")
    
    
]
