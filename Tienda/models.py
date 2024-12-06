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

class Shop(models.Model):
    title = models.CharField(max_length=100,verbose_name="Nombre Producto")
    description = models.TextField(verbose_name="Descripcion")
    image = models.ImageField()
    price = models.IntegerField()
    stock = models.PositiveIntegerField(default=0)  
    author= models.ForeignKey(User,on_delete=models.CASCADE ,verbose_name="Autor")
    classification=models.ManyToManyField(Clasificacion,
                                          verbose_name="Categoria")
    created=models.DateTimeField(auto_now_add=True,
                                verbose_name="Fech Creacion")
    updated=models.DateTimeField(auto_now=True,
                                verbose_name="Fech Edicion")
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

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


class Cotizacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_productos = models.IntegerField()
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
        default='pendiente'
    )

    def __str__(self):
        return f"Cotización {self.cotizacion_id}"

