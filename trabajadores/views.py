from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from .forms import LoginForm  # Define este formulario en trabajadores/forms.py
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, functions, Count
from django.db.models.functions import TruncDay, TruncMonth
from datetime import timedelta
from django.utils.timezone import now
from django.contrib import messages
from Tienda.models import Cotizacion
import json
from login.models import UserProfile
from django.contrib.auth.models import User


# Dashboard del vendedor
from django.db.models import Count

from django.db.models import Count

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

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

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



from django.shortcuts import render
from Tienda.models import Cotizacion

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from Tienda.models import Cotizacion

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

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from Tienda.models import Cotizacion
import json

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

