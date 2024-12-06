from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login_clientes/', views.user_login_clientes, name='login_clientes'),
    path('login_trabajadores/', views.user_login_trabajadores, name='login_trabajadores'),
    path('actualizar_perfil/', views.actualizar_perfil, name='actualizar_perfil'),
    # Ruta para cambiar contraseña
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='login/password_change.html'), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='login/password_change_done.html'), name='password_change_done'),
]

