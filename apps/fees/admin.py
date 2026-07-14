from django.contrib import admin
from .models import FeeStructure, Payment

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('student', 'total_amount', 'total_paid', 'balance_due', 'due_date')
    list_filter = ('due_date',)
    search_fields = ('student__first_name', 'student__last_name')
    date_hierarchy = 'due_date'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('fee_structure', 'amount_paid', 'payment_date', 'recorded_by')
    list_filter = ('payment_date',)
    search_fields = ('fee_structure__student__first_name', 'fee_structure__student__last_name')
    date_hierarchy = 'payment_date'
