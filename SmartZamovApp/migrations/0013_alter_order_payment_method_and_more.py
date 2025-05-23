# Generated by Django 5.1.6 on 2025-02-26 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SmartZamovApp', '0012_order_recipient_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('Cash on delivery', 'In post cash on delivery'), ('On card', 'On card'), ('Crypto', 'On crypto')], max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='recipient_name',
            field=models.CharField(max_length=80, null=True),
        ),
    ]
