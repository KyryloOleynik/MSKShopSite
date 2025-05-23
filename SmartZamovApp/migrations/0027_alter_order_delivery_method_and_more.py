# Generated by Django 5.1.6 on 2025-03-21 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SmartZamovApp', '0026_alter_order_delivery_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_method',
            field=models.CharField(blank=True, choices=[('post_russia', 'Почта России (Россия)'), ('sdek', 'СДЭК (Россия)'), ('courier', 'Сourier (Only for Moscow and Berlin)'), ('dhl', 'DHL (Europe)'), ('ups', 'UPS (Europe)')], max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('cash_on_delivery', 'Cash on delivery'), ('on_card', 'On card'), ('crypto', 'Crypto')], max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('on_cart', 'On cart'), ('pending', 'Pending'), ('completed', 'Completed'), ('active', 'Active'), ('shipped', 'Shipped'), ('canceled', 'Canceled')], default='on_cart', max_length=40),
        ),
    ]
