from django.urls import path
from . import views


app_name = 'budget'

urlpatterns = [
    path('', views.budget_dashboard, name='budget_dashboard'),
    path('section/<int:pk>/', views.section_detail, name='section_detail'),
    path('add-ledger/', views.add_ledger, name='add_ledger'),
    path('add-section/<int:ledger_id>/', views.add_section, name='add_section'),
    path('add-category/', views.add_category, name='add_category'),
    path('section/<int:pk>/edit-budget/', views.edit_section_budget, name='edit_section_budget'),
    path('category/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('expense/<int:pk>/delete/', views.delete_expense, name='delete_expense'),
    path('section/<int:pk>/delete/', views.delete_section, name='delete_section'),
    path('ledger/<int:pk>/delete/', views.delete_ledger, name='delete_ledger'),
    path('ledger/<int:pk>/', views.ledger_detail, name='ledger_detail'),
    path('toggle-income/', views.toggle_income_setting, name='toggle_income_setting'),
    path('ledger/<int:ledger_id>/move/<str:direction>/', views.move_ledger, name='move_ledger'),
    path('section/<int:section_id>/toggle-pin/', views.toggle_pin_section, name='toggle_pin_section'),
]
