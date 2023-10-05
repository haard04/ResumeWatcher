from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('signup',views.signup,name='signup'),
    path('login',views.login,name='login'),
    path('logout',views.logout,name='logout'),
    path('view/<str:username>/', views.view_pdf, name='view_pdf'),
    path('save/<str:filename>/', views.save_pdf, name='save_pdf'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('jobpage',views.jobform,name='jobform'),
    path('add_job_to_profile/<int:user_id>/', views.add_job_to_profile, name='add_job_to_profile'),
    path('get_all_jobs/<int:user_id>/', views.get_all_jobs, name='get_all_jobs'),
    path('getpage',views.getpage,name='getpage')
] 


