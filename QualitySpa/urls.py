"""QualitySpa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls')).
"""
from django.contrib import admin
from django.urls import path, include
from Principal import views as views
from django.conf import settings
from Tienda import views as viewsArticulos
from trabajadores import views as viewsTrabajadores
from login import views as viewsLogin
from django.contrib.auth.views import LogoutView

urlpatterns = [

    # Rutas de la aplicación

    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('send_email/', views.contacto, name='contacto'),
    path('producto/', viewsArticulos.producto, name='producto'),
    path('category/<int:category_id>/', viewsArticulos.category, name='category'),
    
    # Rutas Carrito

    path('carrito/restar/<int:producto_id>/', viewsArticulos.restar_cantidad, name='restar_cantidad'),
    path('carrito/sumar/<int:producto_id>/', viewsArticulos.sumar_cantidad, name='sumar_cantidad'),
    path('producto/<int:id>/', viewsArticulos.producto_detalle, name='producto_detalle'),
    path('agregar-al-carrito/<int:producto_id>/', viewsArticulos.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', viewsArticulos.ver_carrito, name='ver_carrito'),
    path('eliminar-del-carrito/<int:producto_id>/', viewsArticulos.eliminar_del_carrito, name='eliminar_del_carrito'),

    
    path('carrito/update', viewsArticulos.update_cart, name='update_cart'),

    # Rutas del vendedor
    path('vendedor/dashboard/', viewsTrabajadores.dashboard_vendedor, name='dashboard_vendedor'),
    path('vendedor/cotizaciones/', viewsTrabajadores.revisar_cotizaciones, name='revisar_cotizaciones'),
    path('vendedor/historial/', viewsTrabajadores.historial_cotizaciones, name='historial_cotizaciones'),
    path('vendedor/estadisticas/', viewsTrabajadores.estadisticas_ventas, name='estadisticas_ventas'),

    # Rutas de cotizaciones 
    path('vendedor/revisar_cotizaciones/', viewsTrabajadores.revisar_cotizaciones, name='revisar_cotizaciones'),
    path('cotizacion/aprobar/<int:id>/', viewsTrabajadores.aprobar_cotizacion, name='aprobar_cotizacion'),
    path('cotizacion/rechazar/<int:id>/', viewsTrabajadores.rechazar_cotizacion, name='rechazar_cotizacion'),

    path('login/', include('login.urls')),  # Incluir rutas de la app login
    path('dashboard/', viewsLogin.cliente_dashboard, name='cliente_dashboard'),  # Ruta del dashboard
    path('register/', viewsLogin.register, name='register'),  # Ruta para el registro
    path('login/', viewsLogin.user_login, name='login'),  # Ruta para el login
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)