from django import forms
from .models import Business, ComplianceRequest, CorporateBylawsRequest

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

class BusinessRegistrationForm(forms.ModelForm):
    business_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter desired business name'
        })
    )
    business_type = forms.ChoiceField(
        choices=Business.BUSINESS_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    state = forms.ChoiceField(
        choices=Business.STATES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    principal_office_address = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter principal office address'
        })
    )
    registered_agent_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter registered agent name'
        })
    )
    registered_agent_address = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter registered agent address'
        })
    )
    business_purpose = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe the primary business purpose'
        })
    )

    class Meta:
        model = Business
        fields = ['name', 'business_type', 'state']

class AmendmentForm(forms.ModelForm):
    AMENDMENT_TYPES = [
        ('NAME', 'Name Change'),
        ('ADDRESS', 'Address Change'),
        ('AGENT', 'Registered Agent Change'),
        ('PURPOSE', 'Business Purpose Change'),
        ('SHARES', 'Share Structure Change'),
        ('OFFICERS', 'Officers/Directors Change'),
    ]

    amendment_type = forms.ChoiceField(
        choices=AMENDMENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    current_value = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Enter current value'
        })
    )
    new_value = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Enter new value'
        })
    )
    reason_for_change = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Explain the reason for this change'
        })
    )

    class Meta:
        model = ComplianceRequest
        fields = []

class AnnualReportForm(forms.ModelForm):
    principal_office_address = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter principal office address'
        })
    )
    registered_agent_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter registered agent name'
        })
    )
    registered_agent_address = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter registered agent address'
        })
    )
    officers = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List all officers (one per line)'
        })
    )
    directors = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List all directors (one per line)'
        })
    )
    authorized_shares = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter number of authorized shares'
        })
    )
    issued_shares = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter number of issued shares'
        })
    )
    par_value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter par value per share'
        })
    )

    class Meta:
        model = ComplianceRequest
        fields = []

class LLCAnnualReportForm(forms.ModelForm):
    principal_office_address = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter principal office address'
        })
    )
    registered_agent_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter registered agent name'
        })
    )
    registered_agent_address = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter registered agent address'
        })
    )
    members = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List all members (one per line, e.g., "John Smith, 50% ownership")'
        })
    )
    managers = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List all managers (one per line, e.g., "Jane Doe, Managing Member")'
        })
    )
    business_purpose = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe the primary business purpose'
        })
    )
    management_type = forms.ChoiceField(
        choices=[
            ('MEMBER', 'Member-Managed'),
            ('MANAGER', 'Manager-Managed')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    fiscal_year_end = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    total_authorized_capital = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter total authorized capital'
        })
    )
    total_issued_capital = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter total issued capital'
        })
    )
    number_of_members = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter number of members'
        })
    )
    number_of_managers = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter number of managers'
        })
    )
    business_activities = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List all business activities (one per line)'
        })
    )
    foreign_qualifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    foreign_states = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'List states where LLC is qualified to do business'
        })
    )

    class Meta:
        model = ComplianceRequest
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        management_type = cleaned_data.get('management_type')
        number_of_managers = cleaned_data.get('number_of_managers')

        if management_type == 'MANAGER' and number_of_managers == 0:
            raise forms.ValidationError(
                "Manager-managed LLCs must have at least one manager."
            )

        return cleaned_data

class OperatingAgreementForm(forms.ModelForm):
    member_names = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List all members (one per line)'
        })
    )
    ownership_percentages = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List ownership percentages (one per line)'
        })
    )
    management_structure = forms.ChoiceField(
        choices=[
            ('MEMBER', 'Member-Managed'),
            ('MANAGER', 'Manager-Managed')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    capital_contributions = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'List capital contributions (one per line)'
        })
    )
    profit_distribution = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe profit distribution method'
        })
            )

    class Meta:
        model = ComplianceRequest
        fields = []

class FederalEINForm(forms.ModelForm):
    # Choices needed for the form
    SUFFIX_CHOICES = [('', '- Select -'), ('JR', 'Jr.'), ('SR', 'Sr.'), ('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV'), ('V', 'V')]
    SSN_ITIN_TYPE_CHOICES = [('', '- Select -'), ('SSN', 'SSN'), ('ITIN', 'ITIN')]
    LEGAL_STRUCTURE_CHOICES = [
        ('', '- Please Select -'),
        ('SOLE_PROPRIETOR', 'Sole Proprietor'),
        ('PARTNERSHIP', 'Partnership'),
        ('CORPORATION', 'Corporation'),
        ('LLC', 'Limited Liability Company (LLC)'),
        # Add more from "View Additional Types" if needed, e.g. Church, Plan Admin
    ]
    REASON_FOR_EIN_CHOICES = [
        ('', '- Please Select -'),
        ('STARTED_NEW_BUSINESS', 'Started a new business'),
        ('HIRED_EMPLOYEES', 'Hired employee(s)'),
        ('BANKING_PURPOSES', 'Banking purposes'),
        ('CHANGED_TYPE_OF_ORGANIZATION', 'Changed type of organization'),
        ('PURCHASED_ACTIVE_BUSINESS', 'Purchased active business'),
        ('OTHER', 'Other reason'),
    ] # These might need to be dynamic based on legal_structure
    
    US_STATES_TERRITORIES_CHOICES = [
        ('', '- Select -'),
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'),
        ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'),
        ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
        ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
        ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'),
        ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'),
        ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
        ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'),
        ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'),
        ('AS', 'American Samoa'), ('GU', 'Guam'), ('MP', 'Northern Mariana Islands'), ('PR', 'Puerto Rico'), ('VI', 'U.S. Virgin Islands')
    ]
    ACCOUNTING_YEAR_MONTHS = [
        ('', '- Select -'),
        ('JAN', 'January'), ('FEB', 'February'), ('MAR', 'March'), ('APR', 'April'), ('MAY', 'May'), ('JUN', 'June'),
        ('JUL', 'July'), ('AUG', 'August'), ('SEP', 'September'), ('OCT', 'October'), ('NOV', 'November'), ('DEC', 'December')
    ]
    PRIMARY_BUSINESS_ACTIVITY_CHOICES = [ # This needs a comprehensive list based on IRS categories
        ('', '- Please Select -'),
        ('ACCOMMODATION_FOOD', 'Accommodation & Food Services'),
        ('CONSTRUCTION', 'Construction'),
        ('REAL_ESTATE', 'Real Estate, Rental & Leasing'),
        ('RETAIL', 'Retail'),
        ('MANUFACTURING', 'Manufacturing'),
        ('HEALTHCARE_SOCIAL', 'Health Care & Social Assistance'),
        ('FINANCE_INSURANCE', 'Finance & Insurance'),
        ('TRANSPORTATION_WAREHOUSING', 'Transportation & Warehousing'),
        ('WHOLESALE_TRADE', 'Wholesale Trade'),
        ('OTHER_SERVICES', 'Other Services (except Public Administration)'),
        # ... many more categories from IRS instructions for Form SS-4
    ]
    YES_NO_CHOICES = [(True, 'Yes'), (False, 'No')]

    # Applicant Information (New top section)
    applicant_reference_number = forms.CharField(
        max_length=100, required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference Number'}),
        label="Reference Number",
        help_text="(This number can be found on the top right hand corner of your letter)"
    )
    applicant_first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}), label="First Name")
    applicant_last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}), label="Last Name")
    applicant_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}), label="Email")
    applicant_phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}), label="Phone Number")

    # Section 1: Identify Legal Structure
    ein_legal_structure = forms.ChoiceField(
        choices=LEGAL_STRUCTURE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="What type of legal structure is applying for an EIN?"
    )

    # New fields for Sole Proprietor and Partnership
    sole_proprietor_members_count = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Number of members with ownership stake in the LLC, including yourself"
    )

    partnership_type = forms.ChoiceField(
        required=False,
        choices=[
            ('PARTNERSHIP', 'Partnership'),
            ('JOINT_VENTURE', 'Joint Venture')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Please select the type of partnership",
        initial='PARTNERSHIP'
    )

    corporation_type = forms.ChoiceField(
        required=False,
        choices=[
            ('CORPORATION', 'Corporation'),
            ('S_CORPORATION', 'S Corporation')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Please select the type of corporation",
        initial='CORPORATION'
    )

    # Section 2: Responsible Party (Authenticate)
    rp_first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    rp_middle_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name'}))
    rp_last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    rp_suffix = forms.ChoiceField(choices=SUFFIX_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    rp_ssn_itin = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SSN or ITIN (numbers only, no dashes)'}))
    rp_ssn_itin_type = forms.ChoiceField(choices=SSN_ITIN_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Is the number provided SSN or ITIN?")
    responsible_party_title = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title/Position (e.g., Owner, Partner, President)'}))


    # Section 3: LLC Details (Conditional)
    llc_members_count = forms.IntegerField(required=False, min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}), label="Number of members with ownership stake in the LLC, including yourself")
    llc_physical_street = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}))
    llc_physical_apt = forms.CharField(required=False, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apt, Suite, Bldg.'}))
    llc_physical_city = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}))
    llc_physical_state_location = forms.ChoiceField(required=False, choices=US_STATES_TERRITORIES_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="State/Territory where LLC is physically located")
    llc_physical_zip = forms.CharField(required=False, max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP Code'}))

    llc_has_different_mailing_address = forms.ChoiceField(
        choices=[(True, 'Yes'), (False, 'No')], required=False,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}), # Or Select
        label="Do you have an address different from the above where you want your mail to be sent?"
    )
    llc_mail_street = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mailing Street Address'}))
    llc_mail_apt = forms.CharField(required=False, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mailing Apt, Suite, Bldg.'}))
    llc_mail_city = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mailing City'}))
    llc_mail_state = forms.ChoiceField(required=False, choices=US_STATES_TERRITORIES_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Mailing State")
    llc_mail_zip = forms.CharField(required=False, max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mailing ZIP Code'}))

    llc_legal_name_match_articles = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Legal name of LLC (must match articles of organization, if filed)")
    llc_trade_name = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Trade name/Doing business as (only if different from legal name)")
    llc_county_location = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), label="County where LLC is located")
    llc_state_of_organization = forms.ChoiceField(required=False, choices=US_STATES_TERRITORIES_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="State/Territory where articles of organization are (or will be) filed")
    llc_file_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), label="LLC file date with State")
    llc_accounting_year_closing_month = forms.ChoiceField(required=False, choices=ACCOUNTING_YEAR_MONTHS, widget=forms.Select(attrs={'class': 'form-select'}), label="Closing month of accounting year")

    # Section 4: General Business Info / Reasons
    business_start_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), label="Business Start Date or Acquisition Date")
    reason_for_ein = forms.ChoiceField(
        choices=REASON_FOR_EIN_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Why is this entity requesting an EIN?"
    )
    other_reason_text = forms.CharField(
        max_length=255, required=False,
        widget=forms.Textarea(attrs={'class': 'form-control mt-2', 'placeholder': 'Please specify other reason', 'rows': 3})
    )

    # Section 5: Business Activity Questions
    owns_highway_vehicle_55k_lbs = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect, label="Does your business own a highway motor vehicle with a taxable gross weight of 55,000 pounds or more?")
    involves_gambling_wagering = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect, label="Does your business involve gambling/wagering?")
    needs_to_file_form_720 = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect, label="Does your business need to file Form 720 (Quarterly Federal Excise Tax Return)?")
    sells_alcohol_tobacco_firearms = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect, label="Does your business sell or manufacture alcohol, tobacco, or firearms?")
    expects_employees_w2_next_12_months = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect, label="Do you have, or do you expect to have, any employees who will receive Forms W-2 in the next 12 months?")
    primary_business_activity = forms.ChoiceField(choices=PRIMARY_BUSINESS_ACTIVITY_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Primary Business Activity")

    # Add the new field for other business activity
    other_business_activity = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Please specify your primary business activity'
        }),
        label="Please specify your primary business activity"
    )


    class Meta:
        model = ComplianceRequest
        fields = [
            # Applicant Info
            'applicant_reference_number', 'applicant_first_name', 'applicant_last_name', 'applicant_email', 'applicant_phone_number',
            # EIN Form Sections
            'ein_legal_structure', 
            'sole_proprietor_members_count', 'partnership_type', 'corporation_type',
            'rp_first_name', 'rp_middle_name', 'rp_last_name', 'rp_suffix', 'rp_ssn_itin', 'rp_ssn_itin_type', 'responsible_party_title',
            'llc_members_count', 'llc_physical_street', 'llc_physical_apt', 'llc_physical_city', 'llc_physical_state_location', 'llc_physical_zip',
            'llc_has_different_mailing_address', 'llc_mail_street', 'llc_mail_apt', 'llc_mail_city', 'llc_mail_state', 'llc_mail_zip',
            'llc_legal_name_match_articles', 'llc_trade_name', 'llc_county_location', 'llc_state_of_organization', 'llc_file_date', 'llc_accounting_year_closing_month',
            'business_start_date', 'reason_for_ein', 'other_reason_text',
            'owns_highway_vehicle_55k_lbs', 'involves_gambling_wagering', 'needs_to_file_form_720', 'sells_alcohol_tobacco_firearms', 'expects_employees_w2_next_12_months',
            'primary_business_activity', 'other_business_activity',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields not required by default, JS will handle conditional requirement
        # Or set specific fields as not required if they are truly optional independent of JS
        for field_name, field in self.fields.items():
            # Core fields that are always required or have their requirement handled by initial visibility
            always_required_fields = [
                'ein_legal_structure', 
                'rp_first_name', 'rp_last_name', 'rp_ssn_itin', 'rp_ssn_itin_type',
                'business_start_date', 'reason_for_ein'
            ]
            if field_name not in always_required_fields:
                 field.required = False
            
            # Specific labels from the user's text (ensure these match the new workflow if different)
            if field_name == 'applicant_reference_number': 
                field.label = "Reference Number"
                field.help_text = "(This number can be found on the top right hand corner of your letter)"
            if field_name == 'applicant_first_name':
                field.label = "First Name"
            if field_name == 'applicant_last_name':
                field.label = "Last Name"
            if field_name == 'applicant_email':
                field.label = "Email"
            if field_name == 'rp_first_name':
                field.label = "First Name"
            if field_name == 'rp_last_name':
                field.label = "Last Name"
            if field_name == "rp_middle_name":
                field.label = "Middle Name"
            if field_name == "rp_suffix":
                field.label = "Suffix"
            if field_name == 'rp_ssn_itin':
                field.label = "Please provide your SSN or ITIN (# only, no dashes)"
            if field_name == 'llc_file_date':
                field.label = "LLC file date with State"
            if field_name == 'llc_accounting_year_closing_month':
                field.label = "Closing month of accounting year (most common business closing month is December)"
            if field_name == 'ein_legal_structure':
                field.label = "What type of legal structure is applying for an EIN?"
            if field_name == 'llc_members_count':
                field.label = "Number of members with ownership stake in the LLC, including yourself"
            if field_name == 'reason_for_ein': # This label is specific to LLC in the new workflow
                field.label = "Why are you requesting an EIN?" # Will need JS to change if not LLC
            if field_name == 'llc_physical_street':
                field.label = "Street"
            if field_name == 'llc_physical_city':
                field.label = "City"
            if field_name == 'llc_physical_state_location':
                field.label = "State"
            if field_name == 'llc_physical_zip':
                field.label = "Zip Code"
            if field_name == 'llc_has_different_mailing_address':
                field.label = "Do you have an address different from the above where you want your mail to be sent?"
            if field_name == 'llc_legal_name_match_articles':
                field.label = "Legal name of LLC (must match articles of organization, if filed)"
            if field_name == 'llc_trade_name':
                field.label = "Trade name/Doing business as (only if different from legal name)"
            if field_name == 'llc_county_location':
                field.label = "County where LLC is located"
            if field_name == 'llc_state_of_organization':
                field.label = "State/Territory where articles of organization are (or will be) filed"

            # Add placeholders if not already set via widget attrs
            placeholders = {
                'applicant_reference_number': 'Reference Number',
                'applicant_first_name': 'First Name',
                'applicant_last_name': 'Last Name',
                'applicant_email': 'Email',
                'applicant_phone_number': 'Phone Number',
                'rp_first_name': 'First Name',
                'rp_middle_name': 'Middle Name',
                'rp_last_name': 'Last Name',
                'rp_ssn_itin': 'SSN or ITIN',
                'responsible_party_title': 'Title/Position (e.g., Owner, Partner, President)',
                'llc_members_count': 'Number of members',
                'llc_physical_street': 'Street',
                'llc_physical_apt': 'Apt#',
                'llc_physical_city': 'City',
                'llc_physical_zip': 'Zip Code',
                'llc_mail_street': 'Mailing Street',
                'llc_mail_apt': 'Mailing Apt#',
                'llc_mail_city': 'Mailing City',
                'llc_mail_zip': 'Mailing Zip Code',
                'llc_legal_name_match_articles': 'Legal Name of LLC',
                'llc_trade_name': 'Trade Name/Doing business as',
                'llc_county_location': 'County',
            }
            if field_name in placeholders and not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = placeholders[field_name]

class LaborLawPosterForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        }),
        label="First Name"
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        }),
        label="Last Name"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        label="Email"
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        }),
        label="Phone Number"
    )
    reference_number = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Reference Number'
        }),
        label="Reference Number",
        help_text="(This number can be found on the top right hand corner of your letter)"
    )
    business_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Complete Business Name'
        }),
        label="Complete Business Name"
    )


    class Meta:
        model = ComplianceRequest
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'reference_number', 'business_name',
            'agrees_to_terms_digital_signature', 'client_signature_text'
        ]

class CertificateExistenceForm(forms.ModelForm):
    # Requester Details
    requester_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        }),
        label="Full Name"
    )
    requester_address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Address'
        }),
        label="Address"
    )
    requester_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        }),
        label="Phone Number"
    )

    # Business Details
    business_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Exact Business Name'
        }),
        label="Business Name",
        help_text="Must match exactly as shown in Certificate of Formation"
    )
    file_number = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'File Number (Optional)'
        }),
        label="File Number",
        help_text="Company registration number issued by Secretary of State (recommended for faster processing)"
    )

    # Purpose and Additional Requirements
    purpose = forms.ChoiceField(
        choices=[
            ('BANK_ACCOUNT', 'Opening Bank Account'),
            ('BUSINESS_LOAN', 'Business Loan'),
            ('CONTRACT', 'Business Contract'),
            ('LICENSE', 'Business License'),
            ('OTHER', 'Other Purpose')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    additional_requirements = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter any additional requirements or special instructions'
        })
    )

    class Meta:
        model = ComplianceRequest
        fields = [
            'requester_name', 'requester_address', 'requester_phone',
            'business_name', 'file_number',
            'purpose', 'additional_requirements',
        ] 

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

class CorporateBylawsForm(forms.ModelForm):
    corporate_officers = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter each officer\'s name and title on a new line (e.g., "John Smith, President")'
        }),
        help_text='Enter each officer\'s name and title on a new line'
    )
    
    board_of_directors = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter each director\'s name and position on a new line'
        }),
        help_text='Enter each director\'s name and position on a new line'
    )
    
    authorized_shares = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter total number of authorized shares'
        }),
        min_value=1,
        help_text='Total number of authorized shares'
    )
    
    par_value_per_share = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter par value per share (e.g., 0.01)'
        }),
        max_digits=10,
        decimal_places=4,
        min_value=0,
        help_text='Par value per share (e.g., 0.01 for $0.01)'
    )

    class Meta:
        model = CorporateBylawsRequest
        fields = [
            'corporate_officers',
            'board_of_directors',
            'authorized_shares',
            'par_value_per_share'
        ]

    def clean_corporate_officers(self):
        officers = self.cleaned_data.get('corporate_officers')
        if not officers:
            raise forms.ValidationError('Please enter at least one corporate officer.')
        return officers

    def clean_board_of_directors(self):
        directors = self.cleaned_data.get('board_of_directors')
        if not directors:
            raise forms.ValidationError('Please enter at least one board member.')
        return directors

