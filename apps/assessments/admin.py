from django.contrib import admin
from .models import Test, TestResult

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch', 'test_date', 'max_marks', 'created_by')
    list_filter = ('test_date', 'batch')
    search_fields = ('name', 'batch__name', 'created_by__first_name', 'created_by__last_name')
    date_hierarchy = 'test_date'

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('test', 'student', 'marks_obtained')
    list_filter = ('test', 'student')
    search_fields = ('test__name', 'student__full_name')
