from django.urls import path
from . import views


app_name = 'budget'

urlpatterns = [
    path('budget/', views.budget_dashboard, name='budget_dashboard'),
    path('budget/section/<int:pk>/', views.section_detail, name='section_detail'),
    path('budget/add-ledger/', views.add_ledger, name='add_ledger'),
    path('budget/add-section/<int:ledger_id>/', views.add_section, name='add_section'),
    path('budget/add-category/', views.add_category, name='add_category'),
    path('section/<int:pk>/edit-budget/', views.edit_section_budget, name='edit_section_budget'),
    path('category/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('expense/<int:pk>/delete/', views.delete_expense, name='delete_expense'),
    path('section/<int:pk>/delete/', views.delete_section, name='delete_section'),
    path('ledger/<int:pk>/delete/', views.delete_ledger, name='delete_ledger'),
    path('ledger/<int:pk>/', views.ledger_detail, name='ledger_detail'),
]
