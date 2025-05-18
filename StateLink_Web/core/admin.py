from django.contrib import admin

# Register your models here.
from .models import Business, ComplianceRequest

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference_number', 'business_type', 'state_code', 'status', 'date_formed')
    list_filter = ('business_type', 'state_code', 'status', 'is_new', 'missing_filing')
    search_fields = ('name', 'reference_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'reference_number', 'business_type', 'state_code')
        }),
        ('Address Information', {
            'fields': ('address', 'address2', 'city', 'zip_code')
        }),
        ('Business Details', {
            'fields': ('registered_agent', 'date_formed', 'last_filing_date', 'status')
        }),
        ('Status Flags', {
            'fields': ('is_new', 'missing_filing')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ComplianceRequest)
class ComplianceRequestAdmin(admin.ModelAdmin):
    list_display = ('business', 'request_type', 'status', 'price', 'created_at')
    list_filter = ('request_type', 'status')
    search_fields = ('business__name', 'business__reference_number')
    readonly_fields = ('created_at', 'updated_at')