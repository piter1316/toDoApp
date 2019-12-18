from django.urls import path
from . import views


app_name = 'accounts'
urlpatterns = [
    path('accounts/login', views.login_view, name='login'),
    path('accounts/changePassword', views.change_password, name='change_password'),
    path('accounts/changePassword/done', views.change_password, name='change_password_done'),
    path('logout', views.logout_view, name='logout'),
]