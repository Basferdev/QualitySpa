from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login_clientes/', views.user_login_clientes, name='login_clientes'),
    path('login_trabajadores/', views.user_login_trabajadores, name='login_trabajadores'),
]

