from django.urls import path
from . import views
urlpatterns = [
    path('trip_planner/', views.trip_planner, name='trip_planner'),
]