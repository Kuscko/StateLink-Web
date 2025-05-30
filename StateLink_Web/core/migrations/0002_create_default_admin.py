from django.db import migrations
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def create_default_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    # Create superuser if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        User.objects.create(
            username='admin',
            email='admin@statelink.com',
            password=make_password('admin123'),  # You should change this in production
            is_staff=True,
            is_superuser=True,
            is_active=True,
            first_name='Admin',
            last_name='User'
        )

def remove_default_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='admin').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_admin, remove_default_admin),
    ] 