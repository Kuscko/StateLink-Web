from django.db import models
from decimal import Decimal
import uuid

def generate_reference_id():
    """Generate a unique 8-character reference ID"""
    return str(uuid.uuid4())[:8]

# Create your models here.
class Business(models.Model):
    """
    Extended Business model that inherits from the core Business model.
    This allows us to add web-specific fields while maintaining the core functionality.
    """
    # Add any web-specific fields here
    pass

    BUSINESS_TYPES = [
        ('CORP', 'Corporation'),
        ('LLC', 'Limited Liability Company'),
    ]
    
    STATES = [
        ('NC', 'North Carolina'),
        # Add more states as needed
    ]
    
    name = models.CharField(
        max_length=255,
        verbose_name="Business Name",
        help_text="The legal name of the business entity."
    )
    reference_id = models.CharField(
        primary_key=True,
        max_length=255,
        verbose_name="Reference ID",
        help_text="The unique identifier for the business entity.",
        default=generate_reference_id
    )
    business_type = models.CharField(
        max_length=10,
        choices=BUSINESS_TYPES,
        verbose_name="Business Type",
        help_text="Type of business entity."
    )
    address = models.TextField(
        verbose_name="Primary Address",
        help_text="Main business address line 1."
    )
    address2 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Secondary Address",
        help_text="Optional second line of the address."
    )
    city = models.CharField(
        max_length=100,
        verbose_name="City",
        help_text="City where the business is located."
    )
    state_code = models.CharField(
        max_length=2,
        choices=STATES,
        verbose_name="State Code",
        help_text="Two-letter abbreviation for the U.S. state."
    )
    zip_code = models.CharField(
        max_length=10,
        verbose_name="ZIP Code",
        help_text="ZIP or postal code for the business address."
    )
    registered_agent = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Registered Agent",
        help_text="Registered agent of the business."
    )
    date_formed = models.DateField(
        verbose_name="Date Formed",
        help_text="Date the business was legally formed/incorporated."
    )
    last_filing_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Last Filing Date",
        help_text="Date of the last annual report or filing."
    )
    status = models.CharField(
        max_length=50,
        verbose_name="Status",
        help_text="Current status of the business (e.g., Active, Dissolved)."
    )
    is_new = models.BooleanField(
        default=False,
        help_text="Flag for businesses formed in the last 30 days."
    )
    missing_filing = models.BooleanField(
        default=False,
        help_text="True if the business has missed a required filing."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        indexes = [
            models.Index(fields=["state_code"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_new"]),
            models.Index(fields=["missing_filing"]),
            models.Index(fields=["name"]),
            models.Index(fields=["reference_id"]),
            models.Index(fields=["business_type"]),
        ]
        verbose_name = "Business"
        verbose_name_plural = "Businesses"

    def __str__(self):
        return f"{self.name} ({self.get_business_type_display()}) - {self.state_code}"


# Service Request Models
class FederalEINRequest(models.Model):
    LEGAL_STRUCTURE_CHOICES = [
        ('SOLE_PROPRIETORSHIP', 'Sole Proprietorship'),
        ('PARTNERSHIP', 'Partnership'),
        ('JOINT_VENTURE', 'Joint Venture'),
        ('C_CORPORATION', 'C Corporation'),
        ('S_CORPORATION', 'S Corporation'),
        ('LLC', 'Limited Liability Company'),
    ]

    MONTH_CHOICES = [
        ('JANUARY', 'January'),
        ('FEBRUARY', 'February'),
        ('MARCH', 'March'),
        ('APRIL', 'April'),
        ('MAY', 'May'),
        ('JUNE', 'June'),
        ('JULY', 'July'),
        ('AUGUST', 'August'),
        ('SEPTEMBER', 'September'),
        ('OCTOBER', 'October'),
        ('NOVEMBER', 'November'),
        ('DECEMBER', 'December'),
    ]

    REASON_FOR_EIN_CHOICES = [
        ('NEW_BUSINESS', 'New Business'),
        ('HIRED_EMPLOYEES', 'Hired Employees'),
        ('BANKING_PURPOSES', 'Banking Purposes'),
        ('CHANGED_TYPE_OF_ORGANIZATION', 'Changed Type of Organization'),
        ('PURCHASED_BUSINESS', 'Purchased Business'),
        ('OTHER', 'Other'),
    ]

    PRIMARY_BUSINESS_ACTIVITY_CHOICES = [
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
    ]
    
    compliance_request = models.OneToOneField('ComplianceRequest', on_delete=models.CASCADE, related_name='federal_ein_request', null=True, blank=True)

    # EIN Application Structure and Reason
    ein_legal_structure = models.CharField(max_length=50, blank=True, null=True, verbose_name="Type of legal structure applying for EIN")
    members_count = models.IntegerField(blank=True, null=True, verbose_name="Number of members")

    # Responsible Party details
    rp_first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Responsible Party First Name")
    rp_middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Responsible Party Middle Name")
    rp_last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Responsible Party Last Name")
    rp_suffix = models.CharField(max_length=10, blank=True, null=True, verbose_name="Responsible Party Suffix")
    rp_ssn_itin = models.CharField(max_length=11, blank=True, null=True, verbose_name="Responsible Party SSN/ITIN")
    rp_ssn_itin_type = models.CharField(max_length=4, blank=True, null=True, verbose_name="SSN or ITIN")
    responsible_party_title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Responsible Party Title/Position")

    reason_for_ein = models.CharField(max_length=50, blank=True, null=True, verbose_name="Reason for requesting EIN")
    other_reason_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Other reason for EIN, if applicable")

    # LLC Specific Details
    llc_physical_state_location = models.CharField(max_length=2, blank=True, null=True, verbose_name="State/Territory where LLC is physically located")
    llc_physical_street = models.CharField(max_length=255, blank=True, null=True, verbose_name="LLC Physical Street Address")
    llc_physical_apt = models.CharField(max_length=50, blank=True, null=True, verbose_name="LLC Physical Apt/Suite")
    llc_physical_city = models.CharField(max_length=100, blank=True, null=True, verbose_name="LLC Physical City")
    llc_physical_zip = models.CharField(max_length=10, blank=True, null=True, verbose_name="LLC Physical ZIP Code")
    
    llc_has_different_mailing_address = models.BooleanField(null=True, blank=True, verbose_name="Is mailing address different from physical address?")
    llc_mail_street = models.CharField(max_length=255, blank=True, null=True, verbose_name="LLC Mailing Street Address")
    llc_mail_apt = models.CharField(max_length=50, blank=True, null=True, verbose_name="LLC Mailing Apt/Suite")
    llc_mail_city = models.CharField(max_length=100, blank=True, null=True, verbose_name="LLC Mailing City")
    llc_mail_state = models.CharField(max_length=2, blank=True, null=True, verbose_name="LLC Mailing State")
    llc_mail_zip = models.CharField(max_length=10, blank=True, null=True, verbose_name="LLC Mailing ZIP Code")

    llc_legal_name_match_articles = models.CharField(max_length=255, blank=True, null=True, verbose_name="Legal name of LLC (must match articles of organization)")
    llc_trade_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="LLC Trade Name/DBA (if different)")
    llc_county_location = models.CharField(max_length=100, blank=True, null=True, verbose_name="County where LLC is located")
    llc_state_of_organization = models.CharField(max_length=2, blank=True, null=True, verbose_name="State/Territory where articles of organization are (or will be) filed")
    llc_file_date = models.DateField(blank=True, null=True, verbose_name="LLC File Date with State")
    llc_accounting_year_closing_month = models.CharField(choices=MONTH_CHOICES, max_length=20, blank=True, null=True, verbose_name="Closing month of accounting year")

    # Business Start Date
    business_start_date = models.DateField(blank=True, null=True, verbose_name="Business Start Date or Acquisition Date")
    
    # Specific Business Activity Questions (Yes/No)
    owns_highway_vehicle_55k_lbs = models.BooleanField(null=True, blank=True, verbose_name="Owns highway motor vehicle with taxable gross weight of 55,000 pounds or more?")
    involves_gambling_wagering = models.BooleanField(null=True, blank=True, verbose_name="Business involves gambling/wagering?")
    needs_to_file_form_720 = models.BooleanField(null=True, blank=True, verbose_name="Business needs to file Form 720 (Quarterly Federal Excise Tax Return)?")
    sells_alcohol_tobacco_firearms = models.BooleanField(null=True, blank=True, verbose_name="Business sells or manufactures alcohol, tobacco, or firearms?")
    expects_employees_w2_next_12_months = models.BooleanField(null=True, blank=True, verbose_name="Expects to have any employees who will receive Forms W-2 in the next 12 months?")
    
    primary_business_activity = models.CharField(choices=PRIMARY_BUSINESS_ACTIVITY_CHOICES, max_length=100, blank=True, null=True, verbose_name="Primary Business Activity")

    def __str__(self):
        return f"Federal EIN Request for {self.compliance_request.business.name if self.compliance_request else 'No Business'}"

class OperatingAgreementRequest(models.Model):
    MANAGEMENT_STRUCTURE_CHOICES = [
        ('MEMBER_MANAGED', 'Member Managed'),
        ('MANAGER_MANAGED', 'Manager Managed'),
    ]

    compliance_request = models.OneToOneField('ComplianceRequest', on_delete=models.CASCADE, related_name='operating_agreement_request', null=True, blank=True)

    member_names = models.TextField(blank=True, null=True)
    ownership_percentages = models.TextField(blank=True, null=True)
    management_structure = models.CharField(choices=MANAGEMENT_STRUCTURE_CHOICES, max_length=20, blank=True, null=True)
    capital_contributions = models.TextField(blank=True, null=True)
    profit_distribution = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Operating Agreement Request for {self.compliance_request.business.name if self.compliance_request else 'No Business'}"

class CorporateBylawsRequest(models.Model):
    PURPOSE_OF_REQUEST_CHOICES = [
        ('OPEN_BANKING_ACCOUNT', 'Open a bank account'),
        ('BUSINESS_LOAN', 'Business loan'),
        ('BUSINESS_CONTRACT', 'Business contract'),
        ('BUSINESS_LISCENSE', 'Business liscense'),
        ('OTHER_REASON', 'Other reason'),
    ]

    compliance_request = models.OneToOneField('ComplianceRequest', on_delete=models.CASCADE, related_name='corporate_bylaws_request', null=True, blank=True)

    requestor_first_name = models.CharField(max_length=100, blank=True, null=True)
    requestor_last_name = models.CharField(max_length=100, blank=True, null=True)
    requestor_email = models.EmailField(max_length=254, blank=True, null=True)
    requestor_phone_number = models.CharField(max_length=20, blank=True, null=True)
    business_reference_id = models.CharField(max_length=100, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    purpose_of_request = models.CharField(choices=PURPOSE_OF_REQUEST_CHOICES, max_length=255, blank=True, null=True)
    other_reason_text = models.CharField(max_length=255, blank=True, null=True)
    member_names = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Corporate Bylaws Request for {self.compliance_request.business.name if self.compliance_request else 'No Business'}"

class CertificateExistenceRequest(models.Model):
    PURPOSE_OF_REQUEST_CHOICES = [
        ('OPEN_BANKING_ACCOUNT', 'Open a bank account'),
        ('BUSINESS_LOAN', 'Business loan'),
        ('BUSINESS_CONTRACT', 'Business contract'),
        ('BUSINESS_LISCENSE', 'Business liscense'),
        ('OTHER_REASON', 'Other reason'),
    ]

    compliance_request = models.OneToOneField('ComplianceRequest', on_delete=models.CASCADE, related_name='certificate_existence_request', null=True, blank=True)

    requestor_first_name = models.CharField(max_length=100, blank=True, null=True)
    requestor_last_name = models.CharField(max_length=100, blank=True, null=True)
    requestor_email = models.EmailField(max_length=254, blank=True, null=True)
    requestor_phone_number = models.CharField(max_length=20, blank=True, null=True)
    business_reference_id = models.CharField(max_length=100, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    file_number = models.CharField(max_length=100, blank=True, null=True)
    purpose_of_request = models.CharField(choices=PURPOSE_OF_REQUEST_CHOICES, max_length=255, blank=True, null=True)
    other_reason_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Certificate of Existence Request for {self.compliance_request.business.name if self.compliance_request else 'No Business'}"

class LaborLawPosterRequest(models.Model):
    compliance_request = models.OneToOneField('ComplianceRequest', on_delete=models.CASCADE, related_name='labor_law_poster_request', null=True, blank=True)

    requestor_first_name = models.CharField(max_length=100, blank=True, null=True)
    requestor_last_name = models.CharField(max_length=100, blank=True, null=True)
    requestor_email = models.EmailField(max_length=254, blank=True, null=True)
    requestor_phone_number = models.CharField(max_length=20, blank=True, null=True)
    business_reference_id = models.CharField(max_length=100, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Labor Law Poster Request for {self.compliance_request.business.name if self.compliance_request else 'No Business'}"

# Compliance Request Model
class ComplianceRequest(models.Model):
    REQUEST_TYPES = [
        ('ANNUAL_REPORT', 'Annual Report'),
        ('OPERATING_AGREEMENT', 'Operating Agreement'),
        ('CORPORATE_BYLAWS', 'Corporate Bylaws'),
        ('FEDERAL_EIN', 'Federal EIN Application'),
        ('LABOR_LAW_POSTER', 'Labor Law Poster'),
        ('CERTIFICATE_EXISTENCE', 'Certificate of Existence'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('PAYMENT_PENDING', 'Payment Pending'),
        ('PAID', 'Paid'),
    ]

    # Service prices mapping
    SERVICE_PRICES = {
        'ANNUAL_REPORT': Decimal('399.95'),
        'OPERATING_AGREEMENT': Decimal('249.95'),
        'CORPORATE_BYLAWS': Decimal('249.95'),
        'FEDERAL_EIN': Decimal('149.95'),
        'LABOR_LAW_POSTER': Decimal('74.98'),  # Bundled price
        'CERTIFICATE_EXISTENCE': Decimal('74.98'),  # Bundled price
    }
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='compliance_requests')
    request_type = models.CharField(max_length=25, choices=REQUEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Applicant's contact information for THIS request
    applicant_reference_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Applicant Reference Number (from letter)")
    applicant_first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Applicant First Name")
    applicant_last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Applicant Last Name")
    applicant_email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Applicant Email")
    applicant_phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Applicant Phone Number")

    # Agreements and Signature
    agrees_to_terms_digital_signature = models.BooleanField(null=True, blank=True, verbose_name="Agrees to terms and conditions (digital signature representation)")
    client_signature_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Client Agreement Signature (typed name)")
    
    def save(self, *args, **kwargs):
        # Set the price based on request type when saving
        if not self.price:
            self.price = self.SERVICE_PRICES.get(self.request_type, Decimal('0'))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.business.name} - {self.get_request_type_display()} Request"

    def get_total_price(self):
        """Calculate total price of all associated service requests"""
        total = self.price or Decimal('0')
        if hasattr(self, 'federal_ein_request'):
            total += self.SERVICE_PRICES['FEDERAL_EIN']
        if hasattr(self, 'operating_agreement_request'):
            total += self.SERVICE_PRICES['OPERATING_AGREEMENT']
        if hasattr(self, 'corporate_bylaws_request'):
            total += self.SERVICE_PRICES['CORPORATE_BYLAWS']  # Using same price as operating agreement
        if hasattr(self, 'certificate_existence_request'):
            total += self.SERVICE_PRICES['CERTIFICATE_EXISTENCE']
        if hasattr(self, 'labor_law_poster_request'):
            total += self.SERVICE_PRICES['LABOR_LAW_POSTER']
        return total