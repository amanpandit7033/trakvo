from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.FeeListView.as_view(), name='fee_list'),
    path('add/<int:student_id>/', views.FeeStructureCreateView.as_view(), name='fee_add'),
    path('<int:fee_structure_id>/pay/', views.PaymentRecordView.as_view(), name='payment_add'),
    path('receipt/<int:payment_id>/', views.FeeReceiptView.as_view(), name='fee_receipt'),
]
