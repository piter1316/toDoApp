
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Create your views here.
@login_required(login_url='/accounts/login')
def meals(request):
    context = {}
    return render(request, 'meals/index.html', context)

