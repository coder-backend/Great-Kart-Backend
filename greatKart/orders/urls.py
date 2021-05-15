
from django.urls import path
from . import views
urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payment/', views.payment, name='payment'),
    path('makePayment/<int:order_number>/', views.makePayment, name='makePayment'),
    
]
