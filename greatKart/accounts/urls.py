
from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate , name='activate'),
    path('', views.dashboard, name='dashbord'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('forgetPassword/', views.forgetPassword, name = 'forgetPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate , name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name = 'resetPassword'),

]
