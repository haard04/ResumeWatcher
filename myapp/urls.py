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
]


