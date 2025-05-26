from django import forms
from .models import (
    Business, 
    ComplianceRequest,
    FederalEINRequest,
    OperatingAgreementRequest,
    CorporateBylawsRequest,
    CertificateExistenceRequest,
    LaborLawPosterRequest
)

class BusinessSearchForm(forms.Form):
    search_query = forms.CharField(
        label='Search by Reference Number or Business Name',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter reference number or business name'
        })
    )

class ComplianceRequestForm(forms.ModelForm):
    COMPLIANCE_SERVICES = [
        ('OPERATING_AGREEMENT', 'Operating Agreement - $249.95'),
        ('FEDERAL_EIN', 'Federal EIN Application - $149.95'),
        ('LABOR_LAW_POSTER', 'Labor Law Poster - $79.95'),
        ('CORPORATE_BYLAWS', 'Corporate Bylaws - $249.95'),
        ('ANNUAL_REPORT', 'Annual Report - $399.95'),
        ('CERTIFICATE_EXISTENCE', 'Certificate of Existence - $79.95'),
    ]

    services = forms.MultipleChoiceField(
        choices=COMPLIANCE_SERVICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=True,
        help_text='Select all compliance services you need'
    )

    class Meta:
        model = ComplianceRequest
        fields = []

    def clean_services(self):
        services = self.cleaned_data.get('services')
        if not services:
            raise forms.ValidationError('Please select at least one service.')
        return services

class OperatingAgreementForm(forms.ModelForm):
    class Meta:
        model = OperatingAgreementRequest
        fields = [
            'member_names', 'ownership_precentages', 'management_structure',
            'captial_contributions', 'profit_distribution_method'
        ]
        widgets = {
            'management_structure': forms.Select(attrs={'class': 'form-select'}),
            'member_names': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ownership_precentages': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'captial_contributions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profit_distribution_method': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FederalEINForm(forms.ModelForm):
    class Meta:
        model = FederalEINRequest
        fields = [
            'ein_legal_structure', 'members_count',
            'rp_first_name', 'rp_middle_name', 'rp_last_name', 'rp_suffix',
            'rp_ssn_itin', 'rp_ssn_itin_type', 'responsible_party_title',
            'reason_for_ein', 'other_reason_text', 'business_start_date',
            'llc_members_count', 'llc_physical_state_location',
            'llc_physical_street', 'llc_physical_apt', 'llc_physical_city',
            'llc_physical_zip', 'llc_has_different_mailing_address',
            'llc_mail_street', 'llc_mail_apt', 'llc_mail_city',
            'llc_mail_state', 'llc_mail_zip', 'llc_legal_name_match_articles',
            'llc_trade_name', 'llc_county_location', 'llc_state_of_organization',
            'llc_file_date', 'llc_accounting_year_closing_month',
            'owns_highway_vehicle_55k_lbs', 'involves_gambling_wagering',
            'needs_to_file_form_720', 'sells_alcohol_tobacco_firearms',
            'expects_employees_w2_next_12_months', 'primary_business_activity'
        ]
        widgets = {
            'ein_legal_structure': forms.Select(attrs={'class': 'form-select'}),
            'rp_suffix': forms.Select(attrs={'class': 'form-select'}),
            'rp_ssn_itin_type': forms.Select(attrs={'class': 'form-select'}),
            'reason_for_ein': forms.Select(attrs={'class': 'form-select'}),
            'llc_physical_state_location': forms.Select(attrs={'class': 'form-select'}),
            'llc_mail_state': forms.Select(attrs={'class': 'form-select'}),
            'llc_state_of_organization': forms.Select(attrs={'class': 'form-select'}),
            'llc_accounting_year_closing_month': forms.Select(attrs={'class': 'form-select'}),
            'primary_business_activity': forms.Select(attrs={'class': 'form-select'}),
            'business_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'llc_file_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class LaborLawPosterForm(forms.ModelForm):
    class Meta:
        model = LaborLawPosterRequest
        fields = [
            'requestor_first_name', 'requestor_last_name', 'requestor_email',
            'requestor_phone_number', 'business_reference_number', 'business_name'
        ]
        widgets = {
            'requestor_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class CorporateBylawsForm(forms.ModelForm):
    class Meta:
        model = CorporateBylawsRequest
        fields = [
            'requestor_first_name', 'requestor_last_name', 'requestor_email',
            'requestor_phone_number', 'business_reference_number', 'business_name',
            'purpose_of_request', 'other_reason_text', 'additonal_requirements'
        ]
        widgets = {
            'requestor_first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'requestor_last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'requestor_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'requestor_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'business_reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'purpose_of_request': forms.Select(attrs={'class': 'form-select'}),
        }

class CertificateExistenceForm(forms.ModelForm):
    class Meta:
        model = CertificateExistenceRequest
        fields = [
            'requestor_first_name', 'requestor_last_name', 'requestor_email',
            'requestor_phone_number', 'business_reference_number', 'business_name',
            'file_number', 'purpose_of_request', 'other_reason_text',
        ]
        widgets = {
            'purpose_of_request': forms.Select(attrs={'class': 'form-select'}),
        }

class PaymentForm(forms.Form):
    agrees_to_terms_digital_signature = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'agrees_to_terms_digital_signature'
        }),
        label="I agree to the terms and conditions",
        initial=False
    )
    client_signature_text = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type your full name to sign'
        }),
        label="Digital Signature",
        help_text="Type your full name to sign this agreement"
    )

    def save_to_compliance_request(self, compliance_request):
        """Save the agreement and signature to the compliance request"""
        if self.is_valid():
            compliance_request.agrees_to_terms_digital_signature = self.cleaned_data['agrees_to_terms_digital_signature']
            compliance_request.client_signature_text = self.cleaned_data['client_signature_text']
            compliance_request.save()
            return True
        return False

    class Meta:
        model = ComplianceRequest
        fields = [
            'agrees_to_terms_digital_signature', 'client_signature_text'
        ]

