from django.contrib import admin
from .models import Institute, Batch

@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone_number', 'is_suspended', 'trial_ends_on', 'created_at')
    list_filter = ('is_suspended', 'city')
    search_fields = ('name', 'phone_number', 'city')
    date_hierarchy = 'created_at'

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'institute', 'created_at')
    list_filter = ('institute',)
    search_fields = ('name', 'institute__name')
