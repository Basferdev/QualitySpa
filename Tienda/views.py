from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.shortcuts import render,get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
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

def agregar_al_carrito(request, producto_id):
    try:
        # Obtener el producto desde la base de datos
        producto = Shop.objects.get(id=producto_id)
    except Shop.DoesNotExist:
        messages.error(request, "El producto no existe.")
        return redirect('lista_productos')

    # Verificar si hay stock disponible
    if producto.stock <= 0:
        messages.error(request, f'El producto "{producto.title}" no tiene stock disponible.')
        return redirect(request.META.get('HTTP_REFERER', 'lista_productos'))

    # Obtener el carrito desde la sesión (o uno vacío si no existe)
    carrito = request.session.get('carrito', {})

    # Convertir el precio de Decimal a float
    precio_producto = float(producto.price)

    # Si el producto ya está en el carrito, verificar stock antes de incrementar cantidad
    if str(producto.id) in carrito:
        if carrito[str(producto.id)]['cantidad'] < producto.stock:
            carrito[str(producto.id)]['cantidad'] += 1
        else:
            messages.error(request, f'No puedes agregar más unidades de "{producto.title}". Stock insuficiente.')
            return redirect(request.META.get('HTTP_REFERER', 'lista_productos'))
    else:
        # Si no está en el carrito, agregarlo si hay stock
        carrito[str(producto.id)] = {
            'titulo': producto.title,
            'precio': precio_producto,
            'cantidad': 1
        }

    # Guardar el carrito actualizado en la sesión
    request.session['carrito'] = carrito

    # Calcular el total de productos en el carrito (suma de todas las cantidades)
    total_productos = sum(item['cantidad'] for item in carrito.values())

    # Agregar el total de productos al contexto de la sesión
    request.session['total_productos'] = total_productos

    # Mensaje de éxito
    messages.success(request, f'El producto "{producto.title}" se ha añadido al carrito.')

    # Redirigir al usuario a la página anterior
    return redirect(request.META.get('HTTP_REFERER', 'lista_productos'))

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