from django.contrib import admin
from .models import AttendanceRecord

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'batch', 'date', 'status', 'marked_by')
    list_filter = ('status', 'date', 'batch')
    search_fields = ('student__first_name', 'student__last_name', 'batch__name')
    date_hierarchy = 'date'
