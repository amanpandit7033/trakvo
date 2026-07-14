from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'batch', 'institute', 'is_active', 'admission_date')
    list_filter = ('institute', 'batch', 'is_active')
    search_fields = ('full_name', 'phone_number', 'parent_name')
    date_hierarchy = 'admission_date'
