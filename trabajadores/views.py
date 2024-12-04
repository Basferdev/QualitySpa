from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from .forms import LoginForm  # Define este formulario en trabajadores/forms.py
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Cotizacion  # Importa el modelo
from django.db.models import Sum, functions, Count
from django.db.models.functions import TruncDay, TruncMonth
from datetime import timedelta
from django.utils.timezone import now

# Dashboard del vendedor
@login_required
def vendedor_dashboard(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    cotizaciones_entrantes = Cotizacion.objects.filter(estado='pendiente').count()
    cotizaciones_resueltas = Cotizacion.objects.filter(estado='aceptada').count()
    cotizaciones_rechazadas = Cotizacion.objects.filter(estado='rechazada').count()
    total_ventas = Cotizacion.objects.filter(estado='aceptada').aggregate(total=Sum('total'))['total'] or 0

    context = {
        'cotizaciones_entrantes': cotizaciones_entrantes,
        'cotizaciones_resueltas': cotizaciones_resueltas,
        'cotizaciones_rechazadas': cotizaciones_rechazadas,
        'total_ventas': total_ventas,
    }
    return render(request, 'trabajadores/vendedor/dashboard_vendedor.html', context)

# Revisar cotizaciones con datos reales
@login_required
def revisar_cotizaciones(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    cotizaciones = Cotizacion.objects.filter(estado='pendiente')
    return render(request, 'trabajadores/vendedor/revisar_cotizaciones.html', {'cotizaciones': cotizaciones})

# Aprobar cotización
@login_required
def aprobar_cotizacion(request, id):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    cotizacion = Cotizacion.objects.get(id=id)
    cotizacion.estado = 'aceptada'
    cotizacion.save()
    return redirect('revisar_cotizaciones')

# Rechazar cotización
@login_required
def rechazar_cotizacion(request, id):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    cotizacion = Cotizacion.objects.get(id=id)
    cotizacion.estado = 'rechazada'
    cotizacion.save()
    return redirect('revisar_cotizaciones')

# Historial de cotizaciones
@login_required
def historial_cotizaciones(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    historial = Cotizacion.objects.filter(estado__in=['aceptada', 'rechazada']).order_by('-fecha')
    return render(request, 'trabajadores/vendedor/historial_cotizaciones.html', {'historial': historial})

# Estadísticas de ventas
@login_required
def estadisticas_ventas(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    estadisticas = {
        "total_ventas": Cotizacion.objects.filter(estado='aceptada').aggregate(total=Sum('total'))['total'] or 0,
        "numero_cotizaciones": Cotizacion.objects.filter(estado='aceptada').count(),
        "clientes_atendidos": Cotizacion.objects.values('cliente').distinct().count(),
    }
    return render(request, 'trabajadores/vendedor/estadisticas_ventas.html', {'estadisticas': estadisticas})

# Datos para los gráficos
@login_required
def datos_graficos(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    cotizaciones_por_mes = Cotizacion.objects.filter(estado='aceptada').annotate(
        mes=functions.TruncMonth('fecha')
    ).values('mes').annotate(total=Sum('total')).order_by('mes')

    labels = [str(c['mes']) for c in cotizaciones_por_mes]
    data = [c['total'] for c in cotizaciones_por_mes]

    return JsonResponse({'labels': labels, 'data': data})

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

@login_required
def datos_graficos(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Gráfico semanal: cotizaciones de los últimos 7 días
    fecha_actual = now()
    ultimos_7_dias = fecha_actual - timedelta(days=7)
    cotizaciones_semanales = (
        Cotizacion.objects.filter(fecha__gte=ultimos_7_dias)
        .annotate(dia=TruncDay('fecha'))
        .values('dia')
        .annotate(cantidad=Count('id'))
        .order_by('dia')
    )
    labels_semanales = [cotizacion['dia'].strftime('%b %d') for cotizacion in cotizaciones_semanales]
    data_semanales = [cotizacion['cantidad'] for cotizacion in cotizaciones_semanales]

    # Gráfico mensual: ventas totales de los últimos 6 meses
    ultimos_6_meses = fecha_actual - timedelta(days=180)
    ventas_mensuales = (
        Cotizacion.objects.filter(fecha__gte=ultimos_6_meses, estado='aceptada')
        .annotate(mes=TruncMonth('fecha'))
        .values('mes')
        .annotate(total=Sum('total'))
        .order_by('mes')
    )
    labels_mensuales = [venta['mes'].strftime('%B') for venta in ventas_mensuales]
    data_mensuales = [venta['total'] for venta in ventas_mensuales]

    return JsonResponse({
        'semanales': {'labels': labels_semanales, 'data': data_semanales},
        'mensuales': {'labels': labels_mensuales, 'data': data_mensuales},
    })

@login_required
def cotizaciones_entrantes(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Cotizaciones de las últimas 3 horas
    tres_horas_atras = now() - timedelta(hours=3)
    cotizaciones = Cotizacion.objects.filter(fecha__gte=tres_horas_atras, estado='pendiente').order_by('-fecha')

    return render(request, 'trabajadores/vendedor/cotizaciones_entrantes.html', {'cotizaciones': cotizaciones})

@login_required
def cotizaciones_pendientes(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    tres_horas_atras = now() - timedelta(hours=3)
    cotizaciones = Cotizacion.objects.filter(fecha__lt=tres_horas_atras, estado='pendiente').order_by('-fecha')

    return render(request, 'trabajadores/vendedor/cotizaciones_pendientes.html', {'cotizaciones': cotizaciones})

@login_required
def cotizaciones_resueltas(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    cotizaciones = Cotizacion.objects.filter(estado__in=['aceptada', 'rechazada']).order_by('-fecha')

    return render(request, 'trabajadores/vendedor/cotizaciones_resueltas.html', {'cotizaciones': cotizaciones})

@login_required
def cotizaciones_rechazadas(request):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    cotizaciones = Cotizacion.objects.filter(estado='rechazada').order_by('-fecha')

    return render(request, 'trabajadores/vendedor/cotizaciones_rechazadas.html', {'cotizaciones': cotizaciones})

@login_required
def detalle_cotizacion(request, id):
    if not request.user.groups.filter(name='vendedores').exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    cotizacion = Cotizacion.objects.get(id=id)
    return render(request, 'trabajadores/vendedor/detalle_cotizacion.html', {'cotizacion': cotizacion})