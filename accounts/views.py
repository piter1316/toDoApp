from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
# Create your views here.
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from accounts.forms import LoginForm


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                print(request.POST)
                return redirect(request.POST.get('next'))
            else:
                return redirect('todo:index')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('todo:home')
