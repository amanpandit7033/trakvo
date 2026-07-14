from django.urls import path
from . import views

app_name = 'institutes'

urlpatterns = [
    path('profile/', views.InstituteProfileView.as_view(), name='profile'),
    path('batches/', views.BatchListView.as_view(), name='batch_list'),
    path('batches/add/', views.BatchCreateView.as_view(), name='batch_add'),
    path('batches/<int:pk>/edit/', views.BatchUpdateView.as_view(), name='batch_edit'),
    path('batches/<int:pk>/delete/', views.BatchDeleteView.as_view(), name='batch_delete'),
]
