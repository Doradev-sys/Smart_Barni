from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('accounts', '0004_profile_profile_picture')]

    operations = [
        migrations.CreateModel(
            name='CustomerAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, default='', max_length=100)),
                ('recipient_name', models.CharField(blank=True, default='', max_length=150)),
                ('phone', models.CharField(blank=True, default='', max_length=20)),
                ('address_line', models.CharField(max_length=255)),
                ('city', models.CharField(blank=True, default='', max_length=100)),
                ('area', models.CharField(blank=True, default='', max_length=100)),
                ('landmark', models.CharField(blank=True, default='', max_length=255)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-is_default', '-updated_at']},
        ),
    ]
