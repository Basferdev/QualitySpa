from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'Principal/home.html')
def about(request):
    return render(request, 'Principal/about.html')
def contact(request):
    return render(request, 'Principal/contact.html')
