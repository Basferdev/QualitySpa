from django.contrib import admin
from .models import Shop,Clasificacion
# Register your models here.
class ClasificationAdmin(admin.ModelAdmin):
    readonly_fields=('created','updated')

class PostAdmin(admin.ModelAdmin):
    readonly_fields=('created','updated')
admin.site.register(Clasificacion,ClasificationAdmin)
admin.site.register(Shop,PostAdmin)