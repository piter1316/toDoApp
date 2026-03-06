from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='/accounts/login')
def gunsafe_home(request):
    return render(request, 'gunsafe/home.html', {})
