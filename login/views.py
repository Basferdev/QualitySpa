from django.shortcuts import render, redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm, LoginForm
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Asignar al grupo 'clientes'
            group = Group.objects.get(name='clientes')
            user.groups.add(group)
            
            # Autenticar automáticamente
            login(request, user)
            return redirect('cliente_dashboard')  # Redirigir al dashboard del cliente
    else:
        form = RegistrationForm()
    return render(request, 'login/register.html', {'form': form})



@login_required
def cliente_dashboard(request):
    """
    Vista protegida exclusiva para clientes.
    """
    # Validar que el usuario pertenece al grupo 'clientes'
    if not request.user.groups.filter(name='clientes').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Lógica específica para clientes (puedes cargar datos relacionados aquí)
    return render(request, 'login/cliente_dashboard.html')



def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Redirigir según el grupo del usuario
                if user.groups.filter(name='clientes').exists():
                    return redirect('cliente_dashboard')  # Cambia 'cliente_dashboard' por la URL del dashboard de clientes
                else:
                    return redirect('home')  # Redirigir a home si no es cliente
            else:
                form.add_error(None, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'login/login.html', {'form': form})