from django.urls import path
from . import views

app_name = 'gunsafe'
urlpatterns = [
    path('', views.gunsafe_home, name='gunsafe_home'),
    path('archive', views.gunsafe_archive, name='gunsafe_archive'),
    path('weapon/<int:weapon_id>', views.weapon_details, name='weapon_details'),
    path('archive/weapon/<int:weapon_id>', views.archived_weapon_details, name='archived_weapon_details'),
    path('timer', views.shooting_timer, name='shooting_timer'),
    path('timer/save', views.save_timer_result, name='save_timer_result'),
]

