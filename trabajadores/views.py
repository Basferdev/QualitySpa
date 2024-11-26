from django.shortcuts import render, redirect

# Create your views here.

# Vistas del administrador
def dashboard_admin(request):
    return render(request, 'trabajadores/administrador/dashboard_admin.html')

def gestionar_productos(request):
    return render(request, 'trabajadores/administrador/gestionar_productos.html')

def gestionar_usuarios(request):
    return render(request, 'trabajadores/administrador/gestionar_usuarios.html')

def ver_reportes(request):
    return render(request, 'trabajadores/administrador/ver_reportes.html')

# Vistas del vendedor
def dashboard_vendedor(request):
    return render(request, 'trabajadores/vendedor/dashboard_vendedor.html')

def revisar_cotizaciones(request):
    return render(request, 'trabajadores/vendedor/revisar_cotizaciones.html')

def historial_cotizaciones(request):
    return render(request, 'trabajadores/vendedor/historial_cotizaciones.html')

def estadisticas_ventas(request):
    return render(request, 'trabajadores/vendedor/estadisticas_ventas.html')

class Cotizacion:
    def __init__(self, id, cliente, fecha, total, estado):
        self.id = id
        self.cliente = cliente
        self.fecha = fecha
        self.total = total
        self.estado = estado

def revisar_cotizaciones(request):
    # Lista simulada de cotizaciones
    cotizaciones = [
        Cotizacion(1, 'Juan Pérez', '2024-11-17', 1500.00, 'pendiente'),
        Cotizacion(2, 'María López', '2024-11-16', 2000.00, 'aceptada'),
        Cotizacion(3, 'Carlos Ramírez', '2024-11-15', 500.00, 'rechazada'),
    ]
    return render(request, 'trabajadores/vendedor/revisar_cotizaciones.html', {'cotizaciones': cotizaciones})

def aprobar_cotizacion(request, id):
    # Buscar cotización en base de datos y cambiar el estado a 'aceptada'
    return redirect('revisar_cotizaciones')

def rechazar_cotizacion(request, id):
    # Buscar cotización en base de datos y cambiar el estado a 'rechazada'
    return redirect('revisar_cotizaciones')