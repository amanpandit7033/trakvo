from django.contrib import admin
from .models import PlatformPayment, ActivityLog

@admin.register(PlatformPayment)
class PlatformPaymentAdmin(admin.ModelAdmin):
    list_display = ('institute', 'amount', 'payment_date', 'recorded_by')
    list_filter = ('payment_date', 'institute')
    search_fields = ('institute__name', 'notes')
    date_hierarchy = 'payment_date'

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'institute', 'timestamp')
    list_filter = ('timestamp', 'institute')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name', 'action')
    date_hierarchy = 'timestamp'
