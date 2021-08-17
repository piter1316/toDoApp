from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, logout, update_session_auth_hash
# Create your views here.
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from accounts.forms import LoginForm, ChangePasswordForm


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def change_password(request):
    message = ''
    if request.method == 'POST':

        form = ChangePasswordForm(request.user, request.POST)
        form_help = PasswordChangeForm(request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            message = 'Hasło zmienione poprawnie!'

        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ChangePasswordForm(request.user)
        form_help = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {
        'form': form,
        'message': message,
        'form_help': form_help
    })