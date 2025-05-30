from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='compliancerequest',
            name='order_reference_number',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Order Reference Number'),
        ),
    ] 