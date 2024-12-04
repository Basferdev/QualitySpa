from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from Tienda.models import Shop

# Create your views here.
def home(request):
    return render(request, 'Principal/home.html')
def about(request):
    return render(request, 'Principal/about.html')
def contacto(request):
    if request.method == 'POST':
        name=request.POST['name']
        email=request.POST['email']
        subject=request.POST['subject']
        message=request.POST['message']
        template=render_to_string('Principal/email-template.html',{
            'name':name,
            'email':email,
            'subject':subject,
            'message':message
        })
        emailSender=EmailMessage(
            subject,
            template,
            settings.EMAIL_HOST_USER,
            ['correopruebaquality1@gmail.com']
        )
        emailSender.content_subtype ='html'
        emailSender.fail_silently = False
        emailSender.send()
        messages.success(request, 'El correo electrónico se envió correctamente.')

    return redirect('contact')
def contact(request):
    return render(request, 'Principal/contact.html')

def buscar_productos(request):
    query = request.GET.get('q', '').strip()
    productos = []

    if query:
        # Filtrar productos por título o descripción
        productos = Shop.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    return render(request, 'Tienda/buscar.html', {
        'query': query,           # Término de búsqueda
        'productos': productos,   # Productos encontrados
    })