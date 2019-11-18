from django.shortcuts import render


# Create your views here.
def password_generator(request):
    context = {}
    return render(request, 'passwordGenerator/passwordGenerator.html', context)
