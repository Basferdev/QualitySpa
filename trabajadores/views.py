from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group, User
from .forms import LoginForm  # Define este formulario en trabajadores/forms.py
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, functions, Count, Q
from django.db.models.functions import TruncDay, TruncMonth
from datetime import timedelta
from django.utils.timezone import now
from django.contrib import messages
from Tienda.models import Cotizacion
import json
from login.models import UserProfile
from django.utils.timezone import now, timedelta

# Dashboard del vendedor
@login_required
def vendedor_dashboard(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    cotizaciones_entrantes = Cotizacion.objects.filter(estado='pendiente').count()
    cotizaciones_resueltas = Cotizacion.objects.filter(estado='aceptada').count()
    cotizaciones_rechazadas = Cotizacion.objects.filter(estado='rechazada').count()
    total_cotizaciones = Cotizacion.objects.all().count()
    # Obtener las últimas 5 cotizaciones
    historial_reciente = Cotizacion.objects.filter(estado__in=['aceptada', 'rechazada']).order_by('-fecha_creacion')[:5]

    context = {
        'cotizaciones_entrantes': cotizaciones_entrantes,
        'cotizaciones_resueltas': cotizaciones_resueltas,
        'cotizaciones_rechazadas': cotizaciones_rechazadas,
        'total_cotizaciones': total_cotizaciones,
        'historial': historial_reciente,  # Asegúrate de enviar las cotizaciones recientes
    }
    return render(request, 'trabajadores/vendedor/dashboard_vendedor.html', context)

# Revisar cotizaciones con datos reales
@login_required
def revisar_cotizaciones(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Filtrar todas las cotizaciones pendientes (sin asignar vendedor)
    cotizaciones = Cotizacion.objects.filter(estado='pendiente')

    return render(request, 'trabajadores/vendedor/revisar_cotizaciones.html', {'cotizaciones': cotizaciones})

# Aprobar cotización
@login_required
def aprobar_cotizacion(request, id):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Obtener la cotización
    cotizacion = get_object_or_404(Cotizacion, id=id)
    cotizacion.estado = 'aceptada'
    cotizacion.save()
    messages.success(request, "Cotización aprobada exitosamente.")
    return redirect('revisar_cotizaciones')

@login_required
def cotizaciones_resueltas(request):
    cotizaciones = Cotizacion.objects.filter(estado='aceptada')
    context = {'cotizaciones': cotizaciones}
    return render(request, 'trabajadores/vendedor/cotizaciones_aceptadas.html', context)

# Rechazar cotización
@login_required
def rechazar_cotizacion(request, id):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Obtener la cotización
    cotizacion = get_object_or_404(Cotizacion, id=id)
    cotizacion.estado = 'rechazada'
    cotizacion.save()
    messages.success(request, "Cotización rechazada exitosamente.")
    return redirect('revisar_cotizaciones')

@login_required
def cotizaciones_rechazadas(request):
    cotizaciones = Cotizacion.objects.filter(estado='rechazada')
    context = {'cotizaciones': cotizaciones}
    return render(request, 'trabajadores/vendedor/cotizaciones_rechazadas.html', context)

# Historial de cotizaciones
@login_required
def historial_cotizaciones(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Filtrar todas las cotizaciones aceptadas o rechazadas
    historial = Cotizacion.objects.filter(estado__in=['aceptada', 'rechazada']).order_by('-fecha_creacion')
    return render(request, 'trabajadores/vendedor/historial_cotizaciones.html', {'historial': historial})

def trabajador_login(request):
    """
    Vista para el inicio de sesión de trabajadores (vendedores y administradores).
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_superuser:  # Administrador
                    login(request, user)
                    return redirect('/admin/')  # Redirigir al panel de administración
                elif user.groups.filter(name='vendedores').exists():  # Vendedor
                    login(request, user)
                    return redirect('dashboard_vendedor')
                else:
                    form.add_error(None, 'No tienes permiso para acceder como trabajador.')
            else:
                form.add_error(None, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'trabajadores/vendedor/trabajador_login.html', {'form': form})

def cotizaciones_pendientes(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Filtrar cotizaciones pendientes
    cotizaciones = Cotizacion.objects.filter(estado='pendiente')

    # Agregar datos de clientes y fechas
    cotizaciones_datos = []
    for cotizacion in cotizaciones:
        cliente = cotizacion.usuario  # Usuario relacionado

        # Concatenar el nombre y apellido del cliente
        cliente_nombre = f"{cliente.first_name} {cliente.last_name}"

        # Agregar los datos a la lista de cotizaciones
        cotizaciones_datos.append({
            'cotizacion': cotizacion,
            'cliente_nombre': cliente_nombre,
        })

    context = {'cotizaciones': cotizaciones_datos}
    return render(request, 'Tienda/cotizaciones_pendientes.html', context)

@login_required
def detalle_cotizacion(request, id):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Obtener la cotización
    cotizacion = get_object_or_404(Cotizacion, id=id)

    # Obtener el cliente asociado a la cotización
    cliente = cotizacion.usuario

    # Intentar obtener el perfil del cliente desde UserProfile
    try:
        perfil = cliente.profile  # Accede a UserProfile usando la relación OneToOne
        cliente_nombre = f"{cliente.first_name} {cliente.last_name}"
        cliente_telefono = perfil.phone_number  # Accede al número de teléfono
    except UserProfile.DoesNotExist:
        cliente_nombre = f"{cliente.first_name} {cliente.last_name}"
        cliente_telefono = "No disponible"

    # Preparar los datos de los productos desde el JSON almacenado
    productos = json.loads(cotizacion.productos_json)

    # Crear contexto con datos del cliente y la cotización
    context = {
        'cotizacion': cotizacion,
        'productos': productos,
        'cliente_nombre': cliente_nombre,
        'cliente_numero': cliente_telefono,
    }

    return render(request, 'trabajadores/vendedor/detalle_cotizacion.html', context)

# Datos Gráficos
@login_required
def datos_graficos(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Gráfico Semanal: Cotizaciones Totales, Aceptadas y Rechazadas de la última semana (Lunes-Domingo)
    fecha_actual = now()
    inicio_semana = fecha_actual - timedelta(days=fecha_actual.weekday())  # Lunes actual
    dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]  # Lunes a Domingo

    semanales_totales = [
        Cotizacion.objects.filter(fecha_creacion__date=dia).count()
        for dia in dias_semana
    ]
    semanales_aceptadas = [
        Cotizacion.objects.filter(fecha_creacion__date=dia, estado='aceptada').count()
        for dia in dias_semana
    ]
    semanales_rechazadas = [
        Cotizacion.objects.filter(fecha_creacion__date=dia, estado='rechazada').count()
        for dia in dias_semana
    ]
    labels_semanales = [dia.strftime('%A') for dia in dias_semana]

    # Gráfico Mensual: Cotizaciones Totales, Aceptadas y Rechazadas del mes en curso, separado por semanas
    inicio_mes = fecha_actual.replace(day=1)
    semanas_mes = [
        (inicio_mes + timedelta(days=i * 7), inicio_mes + timedelta(days=(i + 1) * 7 - 1))
        for i in range(5)  # Asumimos 5 semanas máximo en un mes
    ]

    mensuales_totales = [
        Cotizacion.objects.filter(fecha_creacion__range=(inicio, fin)).count()
        for inicio, fin in semanas_mes
    ]
    mensuales_aceptadas = [
        Cotizacion.objects.filter(fecha_creacion__range=(inicio, fin), estado='aceptada').count()
        for inicio, fin in semanas_mes
    ]
    mensuales_rechazadas = [
        Cotizacion.objects.filter(fecha_creacion__range=(inicio, fin), estado='rechazada').count()
        for inicio, fin in semanas_mes
    ]
    labels_mensuales = [
        f"Semana {i+1}" for i in range(len(semanas_mes))
    ]

    # Devolver datos en JSON
    return JsonResponse({
        'semanales': {
            'labels': labels_semanales,
            'totales': semanales_totales,
            'aceptadas': semanales_aceptadas,
            'rechazadas': semanales_rechazadas,
        },
        'mensuales': {
            'labels': labels_mensuales,
            'totales': mensuales_totales,
            'aceptadas': mensuales_aceptadas,
            'rechazadas': mensuales_rechazadas,
        },
    })

@login_required
def estadisticas_ventas(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Cálculo de estadísticas
    total_cotizaciones = Cotizacion.objects.count()
    aceptadas = Cotizacion.objects.filter(estado='aceptada').count()
    rechazadas = Cotizacion.objects.filter(estado='rechazada').count()
    pendientes = Cotizacion.objects.filter(estado='pendiente').count()

    # Calcular porcentajes
    porcentaje_aceptadas = (aceptadas / total_cotizaciones) * 100 if total_cotizaciones > 0 else 0
    porcentaje_rechazadas = (rechazadas / total_cotizaciones) * 100 if total_cotizaciones > 0 else 0
    porcentaje_pendientes = (pendientes / total_cotizaciones) * 100 if total_cotizaciones > 0 else 0

    context = {
        'total_cotizaciones': total_cotizaciones,
        'aceptadas': aceptadas,
        'rechazadas': rechazadas,
        'pendientes': pendientes,
        'porcentaje_aceptadas': porcentaje_aceptadas,
        'porcentaje_rechazadas': porcentaje_rechazadas,
        'porcentaje_pendientes': porcentaje_pendientes,
    }

    return render(request, 'trabajadores/vendedor/estadisticas_ventas.html', context)

@login_required
def datos_valores(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Gráfico Semanal: Valores de Cotizaciones Aceptadas (Lunes-Domingo)
    fecha_actual = now()
    inicio_semana = fecha_actual - timedelta(days=fecha_actual.weekday())  # Lunes actual
    dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]  # Lunes a Domingo

    valores_semanales = [
        Cotizacion.objects.filter(fecha_creacion__date=dia, estado='aceptada').aggregate(Sum('total'))['total__sum'] or 0
        for dia in dias_semana
    ]
    labels_semanales = [dia.strftime('%A') for dia in dias_semana]

    # Gráfico Mensual: Valores Aceptados del Mes en Curso (por semanas)
    inicio_mes = fecha_actual.replace(day=1)
    semanas_mes = [
        (inicio_mes + timedelta(days=i * 7), inicio_mes + timedelta(days=(i + 1) * 7 - 1))
        for i in range(4)  # Asumimos 5 semanas máximo en un mes
    ]

    valores_mensuales = [
        Cotizacion.objects.filter(fecha_creacion__range=(inicio, fin), estado='aceptada').aggregate(Sum('total'))['total__sum'] or 0
        for inicio, fin in semanas_mes
    ]
    labels_mensuales = [
        f"Semana {i+1}" for i in range(len(semanas_mes))
    ]

    return JsonResponse({
        'semanales': {
            'labels': labels_semanales,
            'valores': valores_semanales,
        },
        'mensuales': {
            'labels': labels_mensuales,
            'valores': valores_mensuales,
        },
    })
