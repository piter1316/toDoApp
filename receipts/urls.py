from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'receipts'
urlpatterns = [
    path('receipts', views.receipts_home, name='receipts_home'),
    path('receipts/<pk>', views.ReceiptEdit.as_view(), name='receipt'),
    path('create_receipt', views.ReceiptCreateView.as_view(), name='receipt_create'),
    path('receipt_delete/<pk>', views.receipt_delete, name='receipt_delete'),
    # path('receipts/edit/<pk>', views.receipt, name='receipt_edit'),

]
