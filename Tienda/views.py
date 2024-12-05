from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.shortcuts import render,get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
import random
import string
from .models import Shop,Clasificacion,Cotizacion,DetalleCotizacion
from openpyxl import load_workbook
from django.http import HttpResponse
import os

# Create your views here.

from .models import Shop,Clasificacion
def producto(request):
    # Obtener todos los productos
    productos = Shop.objects.all()

    # Obtener todas las categorías disponibles para el filtro
    category_list = Clasificacion.objects.all()

    # Filtrar por categoría si se ha seleccionado una
    category_id = request.GET.get('category')
    if category_id:
        productos = productos.filter(classification__id=category_id)

    # Configuración de la paginación
    paginator = Paginator(productos, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'Tienda/producto.html', {
        'page_obj': page_obj,
        'category_list': category_list,
        'category': category_id,  # Pasar el id de la categoría seleccionada
    })

# Vista para productos de una categoría específica
def category(request, category_id):
    categoria = get_object_or_404(Clasificacion, id=category_id)
    productos = Shop.objects.filter(classification=categoria)

    # Obtener todas las categorías disponibles para el filtro
    category_list = Clasificacion.objects.all()

    # Configuración de la paginación
    paginator = Paginator(productos, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'Tienda/category.html', {
        'page_obj': page_obj,
        'category_list': category_list,
        'category': categoria,  # Pasar el objeto de categoría actual
    })

def producto_detalle(request, id):
    producto = get_object_or_404(Shop, id=id)
    return render(request, 'Tienda/producto_detalle.html', {'producto': producto})

# Ver carrito
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    total_precio = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    return render(request, 'Tienda/carrito.html', {
        'carrito': carrito,
        'total_precio': total_precio,
        'total_productos': sum(item['cantidad'] for item in carrito.values()),
    })

# Eliminar del carrito
def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito
        request.session['total_productos'] = sum(item['cantidad'] for item in carrito.values())
        messages.success(request, "El producto ha sido eliminado del carrito.")
    return redirect('ver_carrito')

# Restar cantidad
def restar_cantidad(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id = str(producto_id)
    if producto_id in carrito and carrito[producto_id]['cantidad'] > 1:
        carrito[producto_id]['cantidad'] -= 1
        request.session['carrito'] = carrito
    elif producto_id in carrito:
        del carrito[producto_id]
        messages.info(request, "El producto fue eliminado porque la cantidad llegó a 0.")
        request.session['carrito'] = carrito
    return redirect('ver_carrito')

# Sumar cantidad    
def sumar_cantidad(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id = str(producto_id)
    if producto_id in carrito:
        carrito[producto_id]['cantidad'] += 1
        request.session['carrito'] = carrito
    return redirect('ver_carrito')

def update_cart(request):

    total_productos = request.session.get('total_productos', 0)
    return JsonResponse({'total_productos': total_productos})

def generar_codigo_cotizacion():
    """Genera un código único para la cotización."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# def generar_excel_cotizacion(cotizacion_id):
#     cotizacion = Cotizacion.objects.get(cotizacion_id=cotizacion_id)

#     # Ruta al archivo de plantilla
#     archivo_plantilla = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'Tienda', 'excel', 'planillaQuality.xlsx')

#     # Cargar la plantilla
#     wb = load_workbook(archivo_plantilla)
#     ws = wb.active

#     # Completar la cotización en el Excel
#     ws['A2'] = cotizacion.cotizacion_id
#     ws['B2'] = cotizacion.usuario.username
#     ws['C2'] = cotizacion.total
#     ws['D2'] = cotizacion.cantidad_productos
#     ws['E2'] = cotizacion.fecha_creacion

#     # Agregar los detalles de los productos
#     fila = 5  # Comenzamos a escribir los productos a partir de la fila 5
#     for detalle in cotizacion.detalles.all():
#         ws[f'A{fila}'] = detalle.producto.title  # Nombre del producto
#         ws[f'B{fila}'] = detalle.producto.price  # Precio unitario
#         ws[f'C{fila}'] = detalle.cantidad  # Cantidad
#         ws[f'D{fila}'] = detalle.precio_total  # Precio total
#         fila += 1

#     # Respuesta HTTP para descargar el archivo Excel
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = f'attachment; filename=cotizacion_{cotizacion.cotizacion_id}.xlsx'
#     wb.save(response)

#     return response

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Shop, Cotizacion

def crear_cotizacion(request):
    if request.method == 'POST':
        # Obtener los productos y cantidades desde el carrito
        carrito = request.session.get('carrito', {})
        if not carrito:
            messages.error(request, "Tu carrito está vacío. No se puede generar una cotización.")
            return redirect('ver_carrito')

        total = 0
        cantidad_productos = 0

        # Crear la cotización
        cotizacion_id = generar_codigo_cotizacion()  # Generar código único para la cotización
        cotizacion = Cotizacion.objects.create(
            usuario=request.user,
            cotizacion_id=cotizacion_id,
            total=total,
            cantidad_productos=cantidad_productos
        )

        # Sumar los totales de los productos seleccionados
        for producto_id, detalles in carrito.items():
            producto = Shop.objects.get(id=producto_id)
            cantidad = detalles['cantidad']
            total += producto.price * cantidad
            cantidad_productos += cantidad

        # Actualizar la cotización con los totales
        cotizacion.total = total
        cotizacion.cantidad_productos = cantidad_productos
        cotizacion.save()

        # Vaciar el carrito
        request.session['carrito'] = {}
        request.session['total_productos'] = 0

        # Mostrar mensaje de éxito
        messages.success(request, "La cotización ha sido generada con éxito.")

        # Redirigir al carrito vacío con el mensaje
        return redirect('ver_carrito')

    return redirect('ver_carrito')  # Si no es un POST, solo redirigimos al carrito


def agregar_al_carrito(request, producto_id):
    try:
        producto = Shop.objects.get(id=producto_id)
    except Shop.DoesNotExist:
        messages.error(request, "El producto no existe.")
        return redirect('lista_productos')

    # Verificar si hay stock disponible
    if producto.stock <= 0:
        messages.error(request, f'El producto "{producto.title}" no tiene stock disponible.')
        return redirect(request.META.get('HTTP_REFERER', 'lista_productos'))

    # Obtener el carrito desde la sesión
    carrito = request.session.get('carrito', {})

    if str(producto.id) in carrito:
        # Verificar stock antes de incrementar la cantidad
        if carrito[str(producto.id)]['cantidad'] < producto.stock:
            carrito[str(producto.id)]['cantidad'] += 1
        else:
            messages.error(request, f'No puedes agregar más unidades de "{producto.title}". Stock insuficiente.')
            return redirect(request.META.get('HTTP_REFERER', 'lista_productos'))
    else:
        carrito[str(producto.id)] = {
            'producto_id': producto.id,
            'titulo': producto.title,
            'precio': float(producto.price),
            'cantidad': 1
        }

    request.session['carrito'] = carrito
    request.session['total_productos'] = sum(item['cantidad'] for item in carrito.values())

    messages.success(request, f'El producto "{producto.title}" se ha añadido al carrito.')
    return redirect(request.META.get('HTTP_REFERER', 'lista_productos'))







