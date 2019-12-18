from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Nazwa użytkownika'},
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control',
               'placeholder': 'Hasło'},
    ))

    class Meta:
        fields = ['Username', 'Password']


class ChangePasswordForm(PasswordChangeForm):

    old_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'},
    ))

    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}
    ))

    new_password2 = forms.CharField(widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        ))

    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']
