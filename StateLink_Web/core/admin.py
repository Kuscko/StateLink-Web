from django.contrib import admin
from .models import (
    Business, 
    ComplianceRequest, 
    FederalEINRequest, 
    OperatingAgreementRequest,
    CorporateBylawsRequest,
    CertificateExistenceRequest,
    LaborLawPosterRequest
)

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference_id', 'business_type', 'state_code', 'status', 'date_formed')
    list_filter = ('business_type', 'state_code', 'status', 'is_new', 'missing_filing')
    search_fields = ('name', 'reference_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'reference_id', 'business_type', 'state_code')
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

class FederalEINRequestInline(admin.StackedInline):
    model = FederalEINRequest
    extra = 0
    fieldsets = (
        ('Legal Structure', {
            'fields': ('ein_legal_structure', 'members_count')
        }),
        ('Responsible Party', {
            'fields': (
                'rp_first_name', 'rp_middle_name', 'rp_last_name', 'rp_suffix',
                'rp_ssn_itin', 'rp_ssn_itin_type', 'responsible_party_title'
            )
        }),
        ('Business Details', {
            'fields': (
                'reason_for_ein', 'other_reason_text', 'business_start_date',
                'primary_business_activity'
            )
        }),
        ('LLC Specific Details', {
            'fields': (
                'llc_physical_state_location',
                'llc_physical_street', 'llc_physical_apt', 'llc_physical_city',
                'llc_physical_zip', 'llc_has_different_mailing_address',
                'llc_mail_street', 'llc_mail_apt', 'llc_mail_city',
                'llc_mail_state', 'llc_mail_zip', 'llc_legal_name_match_articles',
                'llc_trade_name', 'llc_county_location', 'llc_state_of_organization',
                'llc_file_date', 'llc_accounting_year_closing_month'
            )
        }),
        ('Business Activity Questions', {
            'fields': (
                'owns_highway_vehicle_55k_lbs', 'involves_gambling_wagering',
                'needs_to_file_form_720', 'sells_alcohol_tobacco_firearms',
                'expects_employees_w2_next_12_months'
            )
        }),
    )

class OperatingAgreementRequestInline(admin.StackedInline):
    model = OperatingAgreementRequest
    fields = [
        'member_names',
        'ownership_percentages',
        'management_structure',
        'capital_contributions',
        'profit_distribution'
    ]
    extra = 0

class CorporateBylawsRequestInline(admin.StackedInline):
    model = CorporateBylawsRequest
    extra = 0
    fieldsets = (
        ('Corporate Structure', {
            'fields': (
                'corporate_officers',
                'board_of_directors',
                'authorized_shares',
                'par_value_per_share'
            )
        }),
    )

class CertificateExistenceRequestInline(admin.StackedInline):
    model = CertificateExistenceRequest
    extra = 0
    fieldsets = (
        ('Requestor Information', {
            'fields': (
                'requestor_first_name', 'requestor_last_name',
                'requestor_email', 'requestor_phone_number'
            )
        }),
        ('Business Information', {
            'fields': (
                'business_reference_id', 'business_name', 'file_number'
            )
        }),
        ('Request Details', {
            'fields': (
                'purpose_of_request', 'other_reason_text',
            )
        }),
    )

class LaborLawPosterRequestInline(admin.StackedInline):
    model = LaborLawPosterRequest
    extra = 0
    fieldsets = (
        ('Requestor Information', {
            'fields': (
                'requestor_first_name', 'requestor_last_name',
                'requestor_email', 'requestor_phone_number'
            )
        }),
        ('Business Information', {
            'fields': (
                'business_reference_id', 'business_name'
            )
        }),
    )

@admin.register(ComplianceRequest)
class ComplianceRequestAdmin(admin.ModelAdmin):
    list_display = ('business', 'request_type', 'status', 'price', 'order_reference_number', 'created_at', 'unlimited_amendments')
    list_filter = ('request_type', 'status', 'unlimited_amendments')
    search_fields = ('business__name', 'business__reference_id', 'applicant_first_name', 'applicant_last_name', 'order_reference_number')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [
        OperatingAgreementRequestInline,
        FederalEINRequestInline,
        CorporateBylawsRequestInline,
        CertificateExistenceRequestInline,
        LaborLawPosterRequestInline,
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('business', 'request_type', 'status', 'price', 'order_reference_number', 'unlimited_amendments')
        }),
        ('Applicant Information', {
            'fields': (
                'applicant_reference_id', 'applicant_first_name',
                'applicant_last_name', 'applicant_email',
                'applicant_phone_number'
            )
        }),
        ('Agreements', {
            'fields': (
                'agrees_to_terms_digital_signature',
                'client_signature_text'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Register individual service request models for direct access
@admin.register(FederalEINRequest)
class FederalEINRequestAdmin(admin.ModelAdmin):
    list_display = ('compliance_request', 'ein_legal_structure', 'rp_first_name', 'rp_last_name')
    list_filter = ('ein_legal_structure', 'reason_for_ein', 'primary_business_activity')
    search_fields = ('rp_first_name', 'rp_last_name', 'llc_legal_name_match_articles')
    fieldsets = FederalEINRequestInline.fieldsets

@admin.register(OperatingAgreementRequest)
class OperatingAgreementRequestAdmin(admin.ModelAdmin):
    list_display = ('compliance_request', 'management_structure')
    list_filter = ('management_structure',)
    search_fields = ('member_names',)
    fieldsets = OperatingAgreementRequestInline.fieldsets

@admin.register(CorporateBylawsRequest)
class CorporateBylawsRequestAdmin(admin.ModelAdmin):
    list_display = ('compliance_request', 'corporate_officers', 'board_of_directors', 'authorized_shares', 'par_value_per_share')
    search_fields = ('compliance_request__business__name', 'compliance_request__business__reference_id')
    fieldsets = CorporateBylawsRequestInline.fieldsets

@admin.register(CertificateExistenceRequest)
class CertificateExistenceRequestAdmin(admin.ModelAdmin):
    list_display = ('compliance_request', 'business_name', 'requestor_first_name', 'requestor_last_name')
    list_filter = ('purpose_of_request',)
    search_fields = ('business_name', 'requestor_first_name', 'requestor_last_name', 'business_reference_id')
    fieldsets = CertificateExistenceRequestInline.fieldsets

@admin.register(LaborLawPosterRequest)
class LaborLawPosterRequestAdmin(admin.ModelAdmin):
    list_display = ('compliance_request', 'business_name', 'requestor_first_name', 'requestor_last_name')
    search_fields = ('business_name', 'requestor_first_name', 'requestor_last_name', 'business_reference_id')
    fieldsets = LaborLawPosterRequestInline.fieldsets