from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,FileResponse,Http404,JsonResponse,HttpResponseBadRequest
from django.contrib.auth.models import auth,User
from django.contrib import messages
import os
from pathlib import Path
from .models import MyModel,Job
from django.core.files.base import ContentFile
import PyPDF2
import re
import json
import io
import nltk
from rest_framework.decorators import api_view
from rest_framework.response import Response



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

@api_view(['GET'])
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


@api_view(['POST'])
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

@api_view(['POST'])
def add_job_to_profile(request, user_id):
    user = get_object_or_404(MyModel, pk=user_id)

    if request.method == 'POST':
        # Retrieve job details from POST data
        role = request.POST.get('role')
        company_name = request.POST.get('company_name')
        location = request.POST.get('location')
        stipend_amount = request.POST.get('stipend_amount')
        job_type = request.POST.get('job_type')
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
            job_type=job_type,
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

@api_view(['GET'])
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
            'job_type': job.job_type,
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

def update_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    
    if request.method == 'POST':
        # Retrieve updated job details from POST data
        role = request.POST.get('role')
        company_name = request.POST.get('company_name')
        location = request.POST.get('location')
        stipend_amount = request.POST.get('stipend_amount')
        job_type = request.POST.get('job_type')
        application_date = request.POST.get('application_date')
        status = request.POST.get('status')
        job_link = request.POST.get('job_link')
        referred_by = request.POST.get('referred_by')
        
        # Update the job instance
        job.role = role
        job.company_name = company_name
        job.location = location
        job.stipend_amount = stipend_amount
        job.job_type = job_type
        job.application_date = application_date
        job.status = status
        job.job_link = job_link
        job.referred_by = referred_by
        
        # Save the updated job object
        job.save()
        
        return JsonResponse({'message': 'Job successfully updated.'})
    
    return HttpResponseBadRequest('Invalid request method.')

def delete_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    job.delete()
    return JsonResponse({'message': 'Job successfully deleted.'})

@api_view(['GET'])
def get_job_by_id(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    job_data = {
        'job_id': job.job_id, 
        'role': job.role,
        'company_name': job.company_name,
        'location': job.location,
        'stipend_amount': str(job.stipend_amount),
        'job_type': job.job_type,
        'application_date': job.application_date.strftime('%Y-%m-%d'),
        'status': job.status,
        'job_link': job.job_link,
        'referred_by': job.referred_by
    }
    return JsonResponse({'job': job_data})

@api_view(['GET'])
def matchskill(request):
    jobdesc = """
    Job Summary
    About Rubrik

    Rubrik is one of the fastest-growing companies in Silicon Valley, revolutionizing data protection, and management in the emerging multi-cloud world. We are the leader in cloud data management, delivering a single platform to manage and protect data in the cloud, at the edge, and on-premises. Enterprises choose Rubrik to simplify backup and recovery, accelerate cloud adoption, enable automation at scale, and secure against cyberthreats. We’ve been recognized as a Forbes Cloud 100 Company two years in a row and as a LinkedIn Top 10 startup in 2018. 

    Responsibilities

    Design, develop, test, deploy, maintain and improve the software.
    Manage individual projects priorities, deadlines, and deliverables with your technical expertise.
    Identify and solve bottlenecks within our software stack.
    Qualifications

    Rubrik Software Engineer - Interns are self-starters, driven, and can manage themselves.  Bottom line, if you have a limitless drive and like to win, we want to talk to you - come make history! 

    Excellent analytical and mathematics skills
    Ability to work in teams
    Experience programming in Python, Java, Python, C# or C/C++
    Strong understanding of data structures, algorithms, and object-oriented programming
    Strong communication skills
    Eligibility Criteria: 

    Strong programming language skills, and impressive interpersonal abilities so that they can collaborate effectively with other members of their team.
    Applicants must be currently pursuing a Bachelor’s degree or higher in Computer Science / IT, EC, Mathematics and Computing major.
    CGPA 8 and above
    The Internship is scheduled between Jan 2024 - June 2024, and you will be expected to be in our Bangalore office for the entire duration.
    Benefits

    Competitive Stipend
    Flight tickets (within India) booking is provided to travel to Bangalore.
    Breakfast, lunch, dinner, and snacks on a daily basis
    Cab facility within Bangalore
    About Rubrik:

    Rubrik, the Zero Trust Data Security Company™, delivers data security and operational resilience for enterprises. Rubrik’s big idea is to provide data security and data protection on a single platform, including Zero Trust Data Protection, Ransomware Investigation, Incident Containment, Sensitive Data Discovery, and Orchestrated Application Recovery. This means your data is ready so you can recover the data you need, and avoid paying a ransom. Because when you secure your data, you secure your applications, and you secure your business.

    We are a leader in data security, have been recognized as a Forbes Cloud 100 Company, named as a LinkedIn Top 10 Startup and are proud to have earned Great Place to Work® Certification™. There has never been a more exciting time to join Rubrik, and our future is even brighter. The work you do will help propel our next chapter of growth as you do the best work of your career.

    Linkedin | Twitter | Instagram | Rubrik.com | 

    Diversity, Equity & Inclusion @ Rubrik: 

    At Rubrik we are committed to building and sustaining a culture where people of all backgrounds are valued, know they belong, and believe they can succeed here.

    Rubrik's goal is to hire and promote the best person for the job, no matter their background. In doing so, Rubrik is committed to correcting systemic processes and cultural norms that have prevented equal representation. This means we review our current efforts with the intent to offer fair hiring, promotion, and compensation opportunities to people from historically underrepresented communities, and strive to create a company culture where all employees feel they can bring their authentic selves to work and be successful.

    Our DEI strategy focuses on three core areas of our business and culture:

    Our Company: Build a diverse company that provides equitable access to growth and success for all employees globally. 

    Our Culture: Create an inclusive environment where authenticity thrives and people of all backgrounds feel like they belong.

    Our Communities: Expand our commitment to diversity, equity, & inclusion within and beyond our company walls to invest in future generations of underrepresented talent and bring innovation to our clients.

    Equal Opportunity Employer/Veterans/Disabled: Rubrik is an Equal Opportunity Employer. All qualified applicants will receive consideration for employment without regard to race, color, religion, sex, sexual orientation, gender identity, national origin, or protected veteran status and will not be discriminated against on the basis of disability.

    Rubrik provides equal employment opportunities (EEO) to all employees and applicants for employment without regard to race, color, religion, sex, national origin, age, disability or genetics. In addition to federal law requirements, Rubrik complies with applicable state and local laws governing nondiscrimination in employment in every location in which the company has facilities. This policy applies to all terms and conditions of employment, including recruiting, hiring, placement, promotion, termination, layoff, recall, transfer, leaves of absence, compensation and training. 

    Federal law requires employers to provide reasonable accommodation to qualified individuals with disabilities. Please contact us at hr@rubrik.com if you require a reasonable accommodation to apply for a job or to perform your job. Examples of reasonable accommodation include making a change to the application process or work procedures, providing documents in an alternate format, using a sign language interpreter, or using specialized equipment.

    EEO IS THE LAW

    EEO IS THE LAW - POSTER SUPPLEMENT

    PAY TRANSPARENCY NONDISCRIMINATION PROVISION

    NOTIFICATION OF EMPLOYEE RIGHTS UNDER FEDERAL LABOR LAWS
    """
    Skills = ["Python", "Java", "R", "JavaScript", "SQL", "HTML", "CSS", "Machine Learning", "TensorFlow", "Pandas", "Seaborn"]
    Required_skills = getskillsfromdesc(jobdesc)
    matched_words = {'skills': []} 

    def search_pdf_for_words(pdf_file, words):

        pdf_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
            
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()

            for word in words:
                # Use regex for case-insensitive search
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                if re.search(pattern, text):
                    if word not in matched_words['skills']:
                        matched_words['skills'].append(word)

    username = request.user.username

    # Fetch the PDF file path from the MyModel instance
    pdf_instance = MyModel.objects.filter(username=username).first()

        
    if pdf_instance and pdf_instance.pdf_file:
        pdf_file_data = pdf_instance.pdf_file
        pdf_file_bytes = io.BytesIO(pdf_file_data)  # Convert bytes data to a file-like object
        search_pdf_for_words(pdf_file_bytes, Skills)
        
       
        matching_skills = list(set(matched_words['skills']) & set(Required_skills))
        percentage_matched = (len(matching_skills) / len(Required_skills)) * 100
          
        print(f"Required_skills are:{Required_skills}")
        print("Skills in Resume: ", matched_words)
        print("Skills that match with required skills:", matching_skills)
        print(f"{percentage_matched:.2f}% of required skills are matched")
    else:
        print("PDF not found for the user.")
    return render(request,'hello.html') # matched_words,matching_skills,percentage_matched



def getskillsfromdesc(jobdesc):
    # Define a list of common skills
    common_skills = ["Python", "Java", "R", "JavaScript", "SQL", "HTML", "CSS", "Machine Learning", "TensorFlow", "Pandas", "Seaborn"]

    # Extract skills from the job description
    extracted_skills = []

    # Tokenize the text
    words = nltk.word_tokenize(jobdesc)

    # Check for skills in the text
    for skill in common_skills:
        # Use regular expression to match skill names
        pattern = re.compile(re.escape(skill), re.IGNORECASE)
        if any(re.search(pattern, word) for word in words):
            extracted_skills.append(skill)

    # Print the extracted skills
    return extracted_skills

