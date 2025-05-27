from django.db import models
from django.utils import timezone

# Create your models here.
class Business(models.Model):
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
    reference_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Reference Number",
        help_text="Unique reference number for the business."
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
            models.Index(fields=["reference_number"]),
            models.Index(fields=["business_type"]),
        ]
        verbose_name = "Business"
        verbose_name_plural = "Businesses"

    def __str__(self):
        return f"{self.name} ({self.get_business_type_display()}) - {self.state_code}"


class FederalEINRequest(models.Model):
    price = 149.95

    # Responsible Party details
    rp_first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Responsible Party First Name")
    rp_middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Responsible Party Middle Name")
    rp_last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Responsible Party Last Name")
    rp_suffix = models.CharField(max_length=10, blank=True, null=True, verbose_name="Responsible Party Suffix") # Choices like Jr, Sr, I, II, III etc.
    rp_ssn_itin = models.CharField(max_length=11, blank=True, null=True, verbose_name="Responsible Party SSN/ITIN") # Consider encryption
    rp_ssn_itin_type = models.CharField(max_length=4, blank=True, null=True, verbose_name="SSN or ITIN") # Choices: SSN, ITIN
    responsible_party_title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Responsible Party Title/Position") # Existing field, keep for now

    # EIN Application Structure and Reason
    ein_legal_structure = models.CharField(max_length=50, blank=True, null=True, verbose_name="Type of legal structure applying for EIN")
    # Sub-types or confirmations for legal structures can be added if needed, e.g., ein_sole_prop_type
    
    reason_for_ein = models.CharField(max_length=50, blank=True, null=True, verbose_name="Reason for requesting EIN") # Existing general reason
    other_reason_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Other reason for EIN, if applicable") # Existing

    # LLC Specific Details
    llc_members_count = models.IntegerField(blank=True, null=True, verbose_name="Number of LLC Members")
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
    llc_accounting_year_closing_month = models.CharField(max_length=20, blank=True, null=True, verbose_name="Closing month of accounting year") # Choices Jan-Dec

    # Business Start Date (general, was already there)
    business_start_date = models.DateField(blank=True, null=True, verbose_name="Business Start Date or Acquisition Date")

    # Specific Business Activity Questions (Yes/No)
    owns_highway_vehicle_55k_lbs = models.BooleanField(null=True, blank=True, verbose_name="Owns highway motor vehicle with taxable gross weight of 55,000 pounds or more?")
    involves_gambling_wagering = models.BooleanField(null=True, blank=True, verbose_name="Business involves gambling/wagering?")
    needs_to_file_form_720 = models.BooleanField(null=True, blank=True, verbose_name="Business needs to file Form 720 (Quarterly Federal Excise Tax Return)?")
    sells_alcohol_tobacco_firearms = models.BooleanField(null=True, blank=True, verbose_name="Business sells or manufactures alcohol, tobacco, or firearms?")
    expects_employees_w2_next_12_months = models.BooleanField(null=True, blank=True, verbose_name="Expects to have any employees who will receive Forms W-2 in the next 12 months?")
    
    primary_business_activity = models.CharField(max_length=100, blank=True, null=True, verbose_name="Primary Business Activity")

class OperatingAgreementRequest(models.Model):
    price = 249.95

    # Fields for OperatingAgreementForm
    member_names = models.TextField(blank=True, null=True)

class CorporateBylawsRequest(models.Model):
    price = 249.95

    # Fields for CorporateBylawsForm
    corporate_officers = models.TextField(
        verbose_name="Corporate Officers",
        help_text="List of corporate officers with their titles",
        blank=True,
        null=True
    )
    board_of_directors = models.TextField(
        verbose_name="Board of Directors",
        help_text="List of board members with their positions",
        blank=True,
        null=True
    )
    authorized_shares = models.IntegerField(
        verbose_name="Authorized Shares",
        help_text="Total number of authorized shares",
        blank=True,
        null=True
    )
    par_value_per_share = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name="Par Value Per Share",
        help_text="Par value per share",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Corporate Bylaws Request - {self.created_at.strftime('%Y-%m-%d')}"

class CertificateExistenceRequest(models.Model):
    price = 79.95



class LaborLawPosterRequest(models.Model):
    price = 79.95


class ComplianceRequest(models.Model):
    REQUEST_TYPES = [
        ('ANNUAL_REPORT', 'Annual Report'),
        ('OPERATING_AGREEMENT', 'Operating Agreement'),
        ('FEDERAL_EIN', 'Federal EIN Application'),
        ('LABOR_LAW_POSTER', 'Labor Law Poster'),
        ('CERTIFICATE_EXISTENCE', 'Certificate of Existence'),
    ]
    
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('PAID', 'Paid'),
        ('FULLFILLED', 'Fullfilled'),
    ]

    # Service prices mapping
    SERVICE_PRICES = {
        'ANNUAL_REPORT': 399.95,
        'OPERATING_AGREEMENT': 249.95,
        'FEDERAL_EIN': 149.95,
        'LABOR_LAW_POSTER': 149.95,  # Bundled price
        'CERTIFICATE_EXISTENCE': 149.95,  # Bundled price
    }
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='compliance_requests')
    request_type = models.CharField(max_length=25, choices=REQUEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Applicant's contact information for THIS request
    applicant_reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Applicant Reference Number (from letter)")
    applicant_first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Applicant First Name")
    applicant_last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Applicant Last Name")
    applicant_email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Applicant Email")
    applicant_phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Applicant Phone Number")

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='compliance_requests')

    # Agreements and Signature
    agrees_to_terms_digital_signature = models.BooleanField(null=True, blank=True, verbose_name="Agrees to terms and conditions (digital signature representation)")
    client_signature_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Client Agreement Signature (typed name)")
    
    federal_ein_request = models.ForeignKey(FederalEINRequest, on_delete=models.CASCADE, related_name='compliance_requests', null=True, blank=True)
    operating_agreement_request = models.ForeignKey(OperatingAgreementRequest, on_delete=models.CASCADE, related_name='compliance_requests', null=True, blank=True)
    corporate_bylaws_request = models.ForeignKey(CorporateBylawsRequest, on_delete=models.CASCADE, related_name='compliance_requests', null=True, blank=True)
    certificate_existence_request = models.ForeignKey(CertificateExistenceRequest, on_delete=models.CASCADE, related_name='compliance_requests', null=True, blank=True)
    labor_law_poster_request = models.ForeignKey(LaborLawPosterRequest, on_delete=models.CASCADE, related_name='compliance_requests', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Set the price based on request type when saving
        if not self.price:
            self.price = self.SERVICE_PRICES.get(self.request_type, 0)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.business.name} - Compliance Request"