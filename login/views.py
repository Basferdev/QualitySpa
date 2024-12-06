from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group, User
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm, LoginForm
from django.http import HttpResponseForbidden
from .models import UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UpdateProfileForm
from Tienda.models import Cotizacion
from django.db.models import Sum

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Crear el usuario
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()

                # Verificar si ya existe un perfil
                if not hasattr(user, 'profile'):
                    # Crear el perfil de usuario
                    UserProfile.objects.create(
                        user=user,
                        phone_number=form.cleaned_data['phone_number'],
                        address=form.cleaned_data['address'],
                        postal_code=form.cleaned_data['postal_code'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
                    )

                # Asignar al grupo 'clientes'
                group = Group.objects.get(name='clientes')
                user.groups.add(group)

                # Autenticar automáticamente
                login(request, user)
                return redirect('cliente_dashboard')  # Cambia a la URL de tu dashboard de clientes
            except Exception as e:
                # En caso de un error inesperado
                form.add_error(None, f"Ocurrió un error al procesar el registro: {str(e)}")
    else:
        form = RegistrationForm()
    return render(request, 'login/register.html', {'form': form})


@login_required
def cliente_dashboard(request):
    # Verificar si el usuario pertenece al grupo "clientes"
    if not request.user.groups.filter(name='clientes').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Obtener cotizaciones del cliente actual (usuario)
    cotizaciones = Cotizacion.objects.filter(usuario=request.user)

    # Calcular estadísticas
    total_cotizaciones = cotizaciones.count()
    total_gastado = cotizaciones.filter(estado='aceptada').aggregate(total=Sum('total'))['total'] or 0

    context = {
        'cotizaciones': cotizaciones,
        'total_cotizaciones': total_cotizaciones,
        'total_gastado': total_gastado,
    }
    return render(request, 'login/cliente_dashboard.html', context)

@login_required
def actualizar_perfil(request):
    if not request.user.groups.filter(name='clientes').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado exitosamente.")
            return redirect('cliente_dashboard')
    else:
        form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'login/actualizar_perfil.html', {'form': form})


@login_required
def detalle_cotizacion(request, id):
    if not request.user.groups.filter(name='clientes').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    cotizacion = get_object_or_404(Cotizacion, id=id, cliente=request.user)
    return render(request, 'login/detalle_cotizacion.html', {'cotizacion': cotizacion})


def user_login_clientes(request):
    """
    Vista de login para clientes.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                if user.groups.filter(name='clientes').exists():
                    login(request, user)
                    return redirect('cliente_dashboard')  # Redirige al dashboard de clientes
                else:
                    messages.error(request, 'No tienes permiso para acceder como cliente.')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'login/login.html', {'form': form})

def user_login_trabajadores(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Verificar si el usuario es administrador
                if user.groups.filter(name='administradores').exists():
                    # Asegurarse de que tenga un perfil
                    if not hasattr(user, 'profile'):
                        UserProfile.objects.create(
                            user=user,
                            phone_number="0000000000",  # Datos predeterminados
                            address="Dirección predeterminada",
                            postal_code="00000",
                            first_name=user.first_name or "Nombre",
                            last_name=user.last_name or "Apellido"
                        )
                    login(request, user)
                    return redirect('/admin/')  # Redirige al panel de Django

                # Verificar si el usuario es vendedor
                elif user.groups.filter(name='vendedores').exists():
                    # Asegurarse de que tenga un perfil
                    if not hasattr(user, 'profile'):
                        UserProfile.objects.create(
                            user=user,
                            phone_number="0000000000",  # Datos predeterminados
                            address="Dirección predeterminada",
                            postal_code="00000",
                            first_name=user.first_name or "Nombre",
                            last_name=user.last_name or "Apellido"
                        )
                    login(request, user)
                    return redirect('dashboard_vendedor')  # Redirige al dashboard del vendedor
                
                # Usuario no autorizado
                else:
                    form.add_error(None, 'No tienes permiso para acceder como trabajador.')
            else:
                form.add_error(None, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'login/trabajador_login.html', {'form': form})

