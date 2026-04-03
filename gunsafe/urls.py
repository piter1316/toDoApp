from django.urls import path
from . import views

app_name = 'gunsafe'
urlpatterns = [
    path('gunsafe/', views.gunsafe_home, name='gunsafe_home'),
    path('gunsafe/archive', views.gunsafe_archive, name='gunsafe_archive'),
    path('gunsafe/weapon/<int:weapon_id>', views.weapon_details, name='weapon_details'),
    path('gunsafe/archive/weapon/<int:weapon_id>', views.archived_weapon_details, name='archived_weapon_details'),
    path('gunsafe/timer', views.shooting_timer, name='shooting_timer'),
    path('gunsafe/timer/save', views.save_timer_result, name='save_timer_result'),
]

