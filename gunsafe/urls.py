from django.urls import path
from . import views

app_name = 'gunsafe'
urlpatterns = [
    path('gunsafe', views.gunsafe_home, name='gunsafe_home'),
    path('gunsafe/archive', views.gunsafe_archive, name='gunsafe_archive'),
    path('gunsafe/weapon/<int:weapon_id>', views.weapon_details, name='weapon_details'),
]

