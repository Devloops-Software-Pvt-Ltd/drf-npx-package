from django.db import migrations, models
from django.utils import timezone
class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='NpsPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant_id', models.CharField(max_length=255)),
                ('merchant_name', models.CharField(max_length=255)),
                ('api_username', models.CharField(max_length=255)),
                ('api_password', models.CharField(max_length=255)),
                ('gateway_api_secret_key', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
