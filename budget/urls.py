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
]
