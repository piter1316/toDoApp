from django.shortcuts import render


# Create your views here.
def cars_home(request):
    context = {}
    return render(request, 'cars/home.html', context)
