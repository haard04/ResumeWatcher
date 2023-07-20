from django.shortcuts import render,redirect
from django.http import HttpResponse,FileResponse,Http404
from django.contrib.auth.models import auth,User
from django.contrib import messages
import os
from pathlib import Path

# Create your views here.
# admin --- admin
# haardshah04 - Hh@240504

def say_hello(request):  
    return render(request,'hello.html',)

def signup(request):
    if request.method =='POST':
        username= request.POST['username']
        email= request.POST['email']
        password= request.POST['password']
        password2= request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request,'Email Already Used')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,'Username Already Used')
                return redirect('signup')
            else:
                user = User.objects.create_user(username,email,password)
                user.save()
                return redirect('login')
        
        else:
            messages.info(request,'Password Does not match')
            return redirect('signup')
    else:
        return render(request,'signup.html')

def login(request):
    if request.method =='POST':
        username= request.POST['username']
        password= request.POST['password']

        user= auth.authenticate(username = username,password=password)
        
        if user is not None:
            auth.login(request,user)
            return redirect('/profile/'+username)
        else:
            messages.info(request,'Invalid Credentials')
            return redirect('login')
    else:
        return render(request,'login.html')
    
def logout(request):
    auth.logout(request)
    return redirect('/')

def profile(request,username):
    return render(request,'profile.html',{'username':username})

def view_pdf(request, filename):
    pdf_file_path = Path(__file__).resolve().parent.parent / 'pdfs' / filename

    if pdf_file_path.exists() and pdf_file_path.is_file():
        try:
            return FileResponse(open(pdf_file_path, 'rb'), as_attachment=False, content_type='application/pdf')
        except FileNotFoundError:
            raise Http404
    else:
        raise Http404