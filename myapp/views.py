from django.shortcuts import render,redirect
from django.http import HttpResponse,FileResponse,Http404
from django.contrib.auth.models import auth,User
from django.contrib import messages
import os
from pathlib import Path
from .models import MyModel
from django.core.files.base import ContentFile
# Create your views here.
# admin --- admin
# haardshah04 - Hh@240504

def home(request):
    return render(request, 'home.html',)

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
            return redirect('/')
        else:
            messages.info(request,'Invalid Credentials')
            return redirect('login')
    else:
        return render(request,'login.html')
    
def logout(request):
    auth.logout(request)
    return redirect('/')


def upload_pdf(request):
    # Fetch the existing PDF instance for the user's username
    pdf_instance = None
    if request.user.is_authenticated:
        username = request.user.username
        pdf_instance = MyModel.objects.filter(username=username).first()

    return render(request, 'uploadPDF.html', {'user': request.user, 'pdf_instance': pdf_instance})

from django.http import HttpResponse
from .models import MyModel

def view_pdf(request, username):
    try:
        my_model_instance = MyModel.objects.get(username=username)
    except MyModel.DoesNotExist:
        return HttpResponse('PDF not found', status=404)

    if my_model_instance.pdf_file:
        response = HttpResponse(my_model_instance.pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{username}.pdf"'
        return response
    else:
        return HttpResponse('PDF not found', status=404)



def save_pdf(request, filename):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf_file')
        if pdf_file:
            pdf_data = pdf_file.read()

            # Get the username from the form data
            username = request.POST.get('username')

            # Get the value of the 'overwrite_pdf' checkbox
            overwrite_pdf = request.POST.get('overwrite_pdf')

            # Check if a record with the same username already exists
            pdf_instance = MyModel.objects.filter(username=username).first()

            if pdf_instance and overwrite_pdf == 'on':
                # If an existing record is found and user wants to overwrite, update it
                pdf_instance.pdf_file = pdf_data
                pdf_instance.save()
            elif not pdf_instance:
                # If no existing record is found, create a new one
                pdf_instance = MyModel(username=username, pdf_file=pdf_data)
                pdf_instance.save()

            print("SUCCESS")
            return redirect('/')

    # Fetch the existing PDF instance for the user's username
    pdf_instance = None
    if request.user.is_authenticated:
        username = request.user.username
        pdf_instance = MyModel.objects.filter(username=username).first()

    return render(request, 'uploadPDF.html', {'user': request.user, 'pdf_instance': pdf_instance})