from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
import json

# Create your models here.
class Clasificacion(models.Model):
    name=models.CharField(max_length=100,verbose_name="Nombre")
    created=models.DateTimeField(auto_now_add=True,
                                 verbose_name="Fech Creacion")
    updated=models.DateTimeField(auto_now=True,
                                 verbose_name="Fech Edicion")
    
    class Meta:
        verbose_name="Categoria"
        verbose_name_plural="Categorias"
        
    def __str__(self):
        return(self.name)

from django.core.validators import MinValueValidator

class Shop(models.Model):
    title = models.CharField(max_length=100, verbose_name="Nombre Producto")
    description = models.TextField(verbose_name="Descripción")
    image = models.ImageField()
    price = models.IntegerField(
        verbose_name="Precio", 
        validators=[MinValueValidator(1)]  # Valida que el precio mínimo sea 1
    )
    stock = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Autor"
    )
    classification = models.ManyToManyField(
        Clasificacion, 
        verbose_name="Categoría"
    )
    created = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha Creación"
    )
    updated = models.DateTimeField(
        auto_now=True, 
        verbose_name="Fecha Edición"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.title

    

# class Cotizacion(models.Model):
#     usuario = models.ForeignKey(User, on_delete=models.CASCADE)
#     total = models.DecimalField(max_digits=10, decimal_places=2)
#     cantidad_productos = models.IntegerField()
#     cotizacion_id = models.CharField(max_length=100, unique=True)
#     fecha_creacion = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Cotización {self.cotizacion_id}"


from django.core.validators import MinValueValidator

class Cotizacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)],  # Valida que el total sea al menos 1
        verbose_name="Total"
    )
    cantidad_productos = models.IntegerField(
        validators=[MinValueValidator(1)],  # Valida que la cantidad de productos sea al menos 1
        verbose_name="Cantidad de Productos"
    )
    cotizacion_id = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    productos_json = models.TextField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='cotizaciones_pdfs/', null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('aceptada', 'Aceptada'),
            ('rechazada', 'Rechazada'),
        ],
        default='pendiente',
    )
    # Nuevos campos
    cliente_nombre = models.CharField(max_length=50, blank=True, null=True)
    cliente_apellido = models.CharField(max_length=50, blank=True, null=True)
    cliente_telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Cotización {self.cotizacion_id}"



