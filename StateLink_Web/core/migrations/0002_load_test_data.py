from django.db import migrations
from decimal import Decimal
from datetime import date, timedelta

def load_test_data(apps, schema_editor):
    Business = apps.get_model('core', 'Business')
    ComplianceRequest = apps.get_model('core', 'ComplianceRequest')

    # Create test businesses
    businesses = [
        {
            'name': 'Acme Technologies LLC',
            'business_type': 'LLC',
            'reference_id': 'REF001',
            'address': '123 Main Street',
            'address2': 'Suite 100',
            'city': 'Raleigh',
            'state_code': 'NC',
            'zip_code': '27601',
            'registered_agent': 'John Smith',
            'date_formed': date(2024, 1, 15),
            'last_filing_date': date(2024, 1, 15),
            'status': 'ACTIVE',
            'is_new': True,
            'missing_filing': False
        },
        {
            'name': 'Global Solutions Corp',
            'business_type': 'CORP',
            'reference_id': 'REF002',
            'address': '456 Business Park',
            'address2': None,
            'city': 'Charlotte',
            'state_code': 'NC',
            'zip_code': '28202',
            'registered_agent': 'Sarah Johnson',
            'date_formed': date(2023, 6, 1),
            'last_filing_date': date(2024, 1, 1),
            'status': 'ACTIVE',
            'is_new': False,
            'missing_filing': False
        },
        {
            'name': 'Innovative Services LLC',
            'business_type': 'LLC',
            'reference_id': 'REF003',
            'address': '789 Tech Boulevard',
            'address2': 'Unit 200',
            'city': 'Durham',
            'state_code': 'NC',
            'zip_code': '27701',
            'registered_agent': 'Michael Brown',
            'date_formed': date(2023, 12, 1),
            'last_filing_date': date(2023, 12, 1),
            'status': 'ACTIVE',
            'is_new': True,
            'missing_filing': True
        },
        {
            'name': 'Premier Consulting Corp',
            'business_type': 'CORP',
            'reference_id': 'REF004',
            'address': '321 Corporate Center',
            'address2': 'Floor 15',
            'city': 'Greensboro',
            'state_code': 'NC',
            'zip_code': '27401',
            'registered_agent': 'Emily Davis',
            'date_formed': date(2023, 3, 15),
            'last_filing_date': date(2023, 12, 31),
            'status': 'ACTIVE',
            'is_new': False,
            'missing_filing': True
        },
        {
            'name': 'Elite Business Solutions LLC',
            'business_type': 'LLC',
            'reference_id': 'REF005',
            'address': '555 Enterprise Way',
            'address2': None,
            'city': 'Winston-Salem',
            'state_code': 'NC',
            'zip_code': '27101',
            'registered_agent': 'David Wilson',
            'date_formed': date(2024, 2, 1),
            'last_filing_date': date(2024, 2, 1),
            'status': 'ACTIVE',
            'is_new': True,
            'missing_filing': False
        }
    ]

    for business_data in businesses:
        Business.objects.create(**business_data)

def remove_test_data(apps, schema_editor):
    Business = apps.get_model('core', 'Business')
    Business.objects.filter(reference_id__in=['REF001', 'REF002', 'REF003', 'REF004', 'REF005']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_test_data, remove_test_data),
    ] 