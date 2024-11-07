from django.shortcuts import render
from django.core.paginator import Paginator
# Create your views here.
from .models import Shop
def producto(request):
    productos=Shop.objects.all()
    paginator = Paginator(productos,5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "Tienda/producto.html",
     {"page_obj": page_obj}) 

