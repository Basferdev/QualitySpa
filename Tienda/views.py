from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.shortcuts import render,get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
import random
import string
from .models import Shop,Clasificacion,Cotizacion
from openpyxl import load_workbook
from django.http import HttpResponse
import os
import uuid
from django.db import transaction
import json
from django.core.exceptions import ObjectDoesNotExist
from reportlab.pdfgen import canvas
from django.conf import settings
import os

def generar_codigo_cotizacion():
    ultima_cotizacion = Cotizacion.objects.order_by('id').last()
    nuevo_id = 1 if not ultima_cotizacion else ultima_cotizacion.id + 1
    return str(nuevo_id)

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

def crear_cotizacion(request):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        if not carrito:
            messages.error(request, "Tu carrito está vacío. No se puede generar una cotización.")
            return redirect('ver_carrito')

        total = 0
        cantidad_productos = 0
        cotizacion_id = generar_codigo_cotizacion()

        try:
            with transaction.atomic():
                # Crear la cotización sin estado ni vendedor
                cotizacion = Cotizacion(
                    usuario=request.user,
                    cotizacion_id=cotizacion_id,
                    total=0,  # Inicializamos en 0, se actualizará después
                    cantidad_productos=0,
                )
                cotizacion.save()

                productos = []
                for producto_id, detalles in carrito.items():
                    try:
                        producto = Shop.objects.get(id=producto_id)
                    except Shop.DoesNotExist:
                        messages.error(request, f"El producto con ID {producto_id} no existe.")
                        return redirect('ver_carrito')

                    cantidad = detalles['cantidad']
                    precio_unitario = producto.price
                    total += precio_unitario * cantidad
                    cantidad_productos += cantidad

                    # Agregar el producto a la lista de productos
                    productos.append({
                        'producto': producto.title,
                        'cantidad': cantidad,
                        'precio_unitario': precio_unitario
                    })

                # Guardar los productos en formato JSON en la cotización
                cotizacion.productos_json = json.dumps(productos)
                cotizacion.total = total
                cotizacion.cantidad_productos = cantidad_productos
                cotizacion.save()

                # Vaciar el carrito
                request.session['carrito'] = {}
                request.session['total_productos'] = 0

                messages.success(request, "La cotización ha sido generada con éxito.")
                return redirect('ver_carrito')

        except Exception as e:
            messages.error(request, f"Se produjo un error: {str(e)}")
            return redirect('ver_carrito')

    return redirect('ver_carrito')





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



def guardar_detalle_cotizacion(request, cotizacion_id):
    # Verificar que haya productos en el carrito
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "Tu carrito está vacío. No se puede generar el detalle de la cotización.")
        return redirect('ver_carrito')

    try:
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
    except ObjectDoesNotExist:
        messages.error(request, "No se encontró la cotización.")
        return redirect('ver_carrito')

    # Si la cotización existe, actualizamos sus productos
    productos = []
    total = 0
    cantidad_productos = 0

    # Recorrer los productos del carrito y actualizar los detalles
    for producto_id, detalles in carrito.items():
        try:
            producto = Shop.objects.get(id=producto_id)
        except Shop.DoesNotExist:
            messages.error(request, f"El producto con ID {producto_id} no existe.")
            return redirect('ver_carrito')

        cantidad = detalles['cantidad']
        precio_unitario = producto.price
        total += precio_unitario * cantidad
        cantidad_productos += cantidad

        # Agregar cada producto al array de productos
        productos.append({
            'producto': producto.title,
            'cantidad': cantidad,
            'precio_unitario': precio_unitario
        })

    # Guardar los productos en el campo JSON de la cotización
    cotizacion.productos_json = json.dumps(productos)
    cotizacion.total = total
    cotizacion.cantidad_productos = cantidad_productos
    cotizacion.estado = 'Generada'  # Cambiar estado de la cotización
    cotizacion.save()

    # Vaciar el carrito y redirigir al usuario
    request.session['carrito'] = {}
    request.session['total_productos'] = 0

    messages.success(request, "Detalles de la cotización guardados exitosamente.")
    return redirect('ver_carrito')







def generar_pdf_cotizacion(cotizacion):
    # Crear el nombre del archivo
    pdf_filename = f"{cotizacion.cotizacion_id}.pdf"
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'cotizaciones_pdfs')
    pdf_path = os.path.join(pdf_dir, pdf_filename)

    # Crear la carpeta si no existe
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    # Crear el canvas para generar el PDF
    c = canvas.Canvas(pdf_path)

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, f"Cotización #{cotizacion.cotizacion_id}")

    # Información general
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"Usuario: {cotizacion.usuario.username}")
    c.drawString(100, 750, f"Fecha: {cotizacion.fecha_creacion.strftime('%Y-%m-%d')}")

    # Encabezado de la tabla
    c.drawString(100, 720, "Productos:")
    y = 700
    productos = json.loads(cotizacion.productos_json or '[]')

    for producto in productos:
        c.drawString(100, y, f"- {producto['producto']} x {producto['cantidad']} (${producto['precio_unitario']} c/u)")
        y -= 20

    # Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y - 20, f"Total: ${cotizacion.total}")

    # Guardar PDF
    c.save()
    return f"cotizaciones_pdfs/{pdf_filename}"
def crear_cotizacion(request):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        if not carrito:
            messages.error(request, "Tu carrito está vacío. No se puede generar una cotización.")
            return redirect('ver_carrito')

        total = 0
        cantidad_productos = 0
        cotizacion_id = generar_codigo_cotizacion()

        try:
            with transaction.atomic():
                # Crear la cotización
                cotizacion = Cotizacion(
                    usuario=request.user,
                    cotizacion_id=cotizacion_id,
                    total=0,  # Inicializamos en 0, se actualizará después
                    cantidad_productos=0
                )
                cotizacion.save()

                productos = []
                for producto_id, detalles in carrito.items():
                    try:
                        producto = Shop.objects.get(id=producto_id)
                    except Shop.DoesNotExist:
                        messages.error(request, f"El producto con ID {producto_id} no existe.")
                        return redirect('ver_carrito')

                    cantidad = detalles['cantidad']
                    precio_unitario = producto.price
                    total += precio_unitario * cantidad
                    cantidad_productos += cantidad

                    # Agregar el producto a la lista de productos
                    productos.append({
                        'producto': producto.title,
                        'cantidad': cantidad,
                        'precio_unitario': precio_unitario
                    })

                # Guardar los productos en formato JSON en la cotización
                cotizacion.productos_json = json.dumps(productos)
                cotizacion.total = total
                cotizacion.cantidad_productos = cantidad_productos
                cotizacion.save()

                # Generar el PDF
                pdf_path = generar_pdf_cotizacion(cotizacion)
                cotizacion.pdf_file = pdf_path
                cotizacion.save()

                # Vaciar el carrito
                request.session['carrito'] = {}
                request.session['total_productos'] = 0

                messages.success(request, "La cotización ha sido generada con éxito.")
                return redirect('ver_carrito')

        except Exception as e:
            messages.error(request, f"Se produjo un error: {str(e)}")
            return redirect('ver_carrito')

    return redirect('ver_carrito')

from django.http import FileResponse

def descargar_cotizacion_pdf(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, cotizacion_id=cotizacion_id)
    if not cotizacion.pdf_file:
        messages.error(request, "La cotización no tiene un archivo PDF.")
        return redirect('ver_carrito')
    
    return FileResponse(open(cotizacion.pdf_file.path, 'rb'), content_type='application/pdf')    
