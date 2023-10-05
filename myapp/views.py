from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,FileResponse,Http404,JsonResponse
from django.contrib.auth.models import auth,User
from django.contrib import messages
import os
from pathlib import Path
from .models import MyModel,Job
from django.core.files.base import ContentFile


def home(request):
    pdf_instance = MyModel.objects.filter(username=request.user.username).first()
    view_count = pdf_instance.view_count if pdf_instance else 0

    
    
    if request.method == 'POST':
        username = request.POST.get('viewuser')
        return redirect('/view/' + username)
    else:
        return render(request, 'home.html', {'pdf_instance': pdf_instance,'view_count': view_count})
    
    
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
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(os.path.join(BASE_DIR, 'db.sqlite3'))
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
    
    my_model_instance.view_count += 1
    my_model_instance.save()

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

def jobform(request):
    user_id = request.user.id
    return render(request,'createjob.html',{'user_id': user_id})


def add_job_to_profile(request, user_id):
    user = get_object_or_404(MyModel, pk=user_id)

    if request.method == 'POST':
        # Retrieve job details from POST data
        role = request.POST.get('role')
        company_name = request.POST.get('company_name')
        location = request.POST.get('location')
        stipend_amount = request.POST.get('stipend_amount')
        application_no = request.POST.get('application_no')
        application_date = request.POST.get('application_date')
        status = request.POST.get('status')
        job_link = request.POST.get('job_link')
        referred_by = request.POST.get('referred_by')

        # Create a new job instance
        job = Job.objects.create(
            role=role,
            company_name=company_name,
            location=location,
            stipend_amount=stipend_amount,
            application_no=application_no,
            application_date=application_date,
            status=status,
            job_link=job_link,
            referred_by=referred_by
        )

        # Associate the job with the user
        user.job_ids.add(job)

        # Save both user and job objects
        user.save()
        job.save()

        return JsonResponse({'message': 'Job successfully added to the user profile.'})

    return JsonResponse({'message': 'Invalid request method.'})

def get_all_jobs(request, user_id):
    # Get the MyModel instance based on user ID
    user_instance = get_object_or_404(MyModel, pk=user_id)

    # Fetch jobs associated with the user using subquery
    jobs = Job.objects.filter(job_id__in=user_instance.job_ids.values('job_id'))

    # Create a list to store job details
    jobs_array = []
    for job in jobs:
        job_data = {
            'job_id': job.job_id,
            'role': job.role,
            'company_name': job.company_name,
            'location': job.location,
            'stipend_amount': str(job.stipend_amount),
            'application_no': job.application_no,
            'application_date': job.application_date.strftime('%Y-%m-%d'),
            'status': job.status,
            'job_link': job.job_link,
            'referred_by': job.referred_by
        }
        jobs_array.append(job_data)

        print(jobs_array)

    return JsonResponse({'jobs': jobs_array})


def getpage(request):
    user_id = request.user.id
    return render(request,'getpage.html',{'USER_ID': user_id})