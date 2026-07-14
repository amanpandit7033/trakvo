from django.urls import path
from . import views

app_name = 'platform_admin'

urlpatterns = [
    path('dashboard/', views.PlatformDashboardView.as_view(), name='dashboard'),
    
    path('institutes/', views.InstituteAdminListView.as_view(), name='institute_list'),
    path('institutes/create/', views.InstituteCreateView.as_view(), name='institute_create'),
    path('institutes/<int:pk>/', views.InstituteAdminDetailView.as_view(), name='institute_detail'),
    path('institutes/<int:pk>/suspend/', views.SuspendInstituteView.as_view(), name='suspend_institute'),
    path('institutes/<int:pk>/extend-trial/', views.ExtendTrialView.as_view(), name='extend_trial'),
    
    path('users/', views.UserAdminListView.as_view(), name='user_list'),
    path('users/<int:pk>/reset-password/', views.UserResetPasswordView.as_view(), name='user_reset_password'),
    path('users/<int:pk>/deactivate/', views.UserDeactivateView.as_view(), name='user_deactivate'),
    
    path('institutes/<int:pk>/payments/', views.PlatformPaymentListView.as_view(), name='payment_list'),
    path('institutes/<int:pk>/payments/add/', views.PlatformPaymentCreateView.as_view(), name='payment_create'),
    
    path('activity/', views.ActivityLogListView.as_view(), name='activity_list'),
]
