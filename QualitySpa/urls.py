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
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Principal import views as views
from django.conf import settings
from Tienda import views as viewsArticulos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('producto/', viewsArticulos.producto, name='producto'),
    path('category/<int:category_id>/', viewsArticulos.category, name='category'),
     # Rutas del administrador
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('admin/gestionar_productos/', views.gestionar_productos, name='gestionar_productos'),
    path('admin/gestionar_usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('admin/ver_reportes/', views.ver_reportes, name='ver_reportes'),

    # Rutas del vendedor
    path('dashboard/vendedor/', views.dashboard_vendedor, name='dashboard_vendedor'),
    path('vendedor/revisar_cotizaciones/', views.revisar_cotizaciones, name='revisar_cotizaciones'),
    path('vendedor/historial_cotizaciones/', views.historial_cotizaciones, name='historial_cotizaciones'),
    path('vendedor/estadisticas_ventas/', views.estadisticas_ventas, name='estadisticas_ventas'),
    
]

    
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)