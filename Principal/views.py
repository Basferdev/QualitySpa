from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'Principal/home.html')
def about(request):
    return render(request, 'Principal/about.html')
def contact(request):
    return render(request, 'Principal/contact.html')

# Vistas del administrador
def dashboard_admin(request):
    return render(request, 'Principal/administrador/dashboard_admin.html')

def gestionar_productos(request):
    return render(request, 'Principal/administrador/gestionar_productos.html')

def gestionar_usuarios(request):
    return render(request, 'Principal/administrador/gestionar_usuarios.html')

def ver_reportes(request):
    return render(request, 'Principal/administrador/ver_reportes.html')

# Vistas del vendedor
def dashboard_vendedor(request):
    return render(request, 'Principal/vendedor/dashboard_vendedor.html')

def revisar_cotizaciones(request):
    return render(request, 'Principal/vendedor/revisar_cotizaciones.html')

def historial_cotizaciones(request):
    return render(request, 'Principal/vendedor/historial_cotizaciones.html')

def estadisticas_ventas(request):
    return render(request, 'Principal/vendedor/estadisticas_ventas.html')