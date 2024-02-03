from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.

def UserLogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        user_obj = User.objects.filter(username=email).first()
        
        if user_obj is None:
            messages.success(request, "User Not Found")
            return redirect('login')
        
        user = authenticate(username=email, password=password)
        
        if user is None:
            messages.success(request, "Wrong Password")
            return redirect('login')
        
        login(request, user)
        
        next_url = request.GET.get('next')
        
        if next_url:
            return redirect(next_url)
        else:
            return redirect('index')
    
    return render(request, "Account/login.html")




def UserRegister(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        if User.objects.filter(username=username).exists():         
            messages.success(request,"Usename already taken")
            return redirect('register')
        
        if User.objects.filter(email=email).exists():         
            messages.success(request,"Email already taken")
            return redirect('register')
 
        user = User.objects.create_user(username=username,password=password,email=email)
        user.save()
            
        return redirect("login")       
        
        
    return render(request,'Account/register.html')

def UserLogout(request):
    logout(request)
    return redirect("index")


def UserSetting(request):
    return render(request,'Account/setting.html')

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)




