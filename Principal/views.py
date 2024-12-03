from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
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