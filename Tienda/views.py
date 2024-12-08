from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.shortcuts import render,get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Shop,Clasificacion,Cotizacion
from openpyxl import load_workbook
from django.http import HttpResponse
import os
from django.db import transaction
import json
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.platypus.flowables import Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.staticfiles import finders 

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

    # Crear el documento PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    elementos = []

    # Agregar logo con fondo negro en la esquina superior izquierda
    def agregar_logo(canvas, doc):
        # Buscar el archivo logo.png en la carpeta estática
        logo_path = finders.find('Tienda/logo.jpeg')  # Buscar archivo en static/Tienda/logo.png
        if logo_path:  # Verificar si se encuentra el archivo
            canvas.saveState()

            # Dibujar solo el logo (sin fondo negro)
            lado_cuadrado = 100  # Tamaño del lado del cuadrado (ajustar según lo necesario)
            canvas.drawImage(logo_path, 25, 735, width=lado_cuadrado, height=lado_cuadrado, mask='auto')

            canvas.restoreState()
        else:
            print("No se encontró el archivo logo.png en static/Tienda/")

    # Estilos y título
    styles = getSampleStyleSheet()
    titulo_estilo = styles['Heading1']
    elementos.append(Paragraph(f"Cotización #{cotizacion.cotizacion_id}", titulo_estilo))

    # Información general
    info_estilo = styles['Normal']
    elementos.append(Paragraph(f"Nombre: {cotizacion.usuario.first_name} {cotizacion.usuario.last_name}", info_estilo))
    elementos.append(Paragraph(f"Fecha: {cotizacion.fecha_creacion.strftime('%d-%m-%Y')}", info_estilo))
    # Agregar el número de teléfono
    phone_number = cotizacion.usuario.profile.phone_number  # Acceder al número de teléfono desde el perfil del usuario
    elementos.append(Paragraph(f"Teléfono: {phone_number}", info_estilo))
    elementos.append(Spacer(1, 20))  # Espacio antes de la tabla

    # Productos como tabla
    productos = json.loads(cotizacion.productos_json or '[]')
    data = [["Producto", "Cantidad", "Precio Unitario", "Subtotal"]]
    for producto in productos:
        data.append([ 
            producto['producto'],
            producto['cantidad'],
            f"${producto['precio_unitario']}",
            f"${producto['cantidad'] * producto['precio_unitario']}"
        ])

    # Estilo de la tabla
    tabla = Table(data, colWidths=[200, 100, 100, 100])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ]))
    elementos.append(tabla)

    # Calcular el IVA (19%)
    iva = int(cotizacion.total * 0.19)  # IVA del 19%, convertido a entero
    total_con_iva = cotizacion.total   # El total es el neto más el IVA

    # Agregar detalles del IVA y Total
    elementos.append(Spacer(1, 20))  # Espacio entre la tabla y los totales
    elementos.append(Paragraph(f"<b>IVA (19%):</b> ${iva}", info_estilo))
    elementos.append(Paragraph(f"<b>Total:</b> ${total_con_iva}", info_estilo))

    # Generar el PDF
    doc.build(elementos, onFirstPage=agregar_logo)

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
                # Verificar si el usuario tiene un perfil asociado
                perfil = None
                if hasattr(request.user, 'profile'):
                    perfil = request.user.profile

                # Crear la cotización con datos adicionales del cliente
                cotizacion = Cotizacion(
                    usuario=request.user,
                    cotizacion_id=cotizacion_id,
                    total=0,  # Se actualizará después
                    cantidad_productos=0,
                    cliente_nombre=request.user.first_name,  # Se obtiene del usuario logueado
                    cliente_apellido=request.user.last_name,  # Se obtiene del usuario logueado
                    cliente_telefono=perfil.phone_number if perfil else "No disponible",  # Verifica si hay un perfil
                )
                cotizacion.save()

                productos = []
                for producto_id, detalles in carrito.items():
                    try:
                        producto = Shop.objects.get(id=producto_id)
                    except Shop.DoesNotExist:
                        messages.error(request, f"El producto con ID {producto_id} no existe.")
                        return redirect('ver_carrito')

                    cantidad = detalles.get('cantidad', 1)
                    precio_unitario = producto.price
                    total += precio_unitario * cantidad
                    cantidad_productos += cantidad

                    # Agregar cada producto al array de productos
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


def descargar_cotizacion_pdf(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, cotizacion_id=cotizacion_id)
    if not cotizacion.pdf_file:
        messages.error(request, "La cotización no tiene un archivo PDF.")
        return redirect('ver_carrito')
    
    return FileResponse(open(cotizacion.pdf_file.path, 'rb'), content_type='application/pdf')    
