# Generated by Django 5.1.7 on 2025-03-27 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SmartZamovApp', '0032_rename_average_price_in_stores_product_price_without_sale_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='slug',
            field=models.SlugField(default=1, unique=True),
            preserve_default=False,
        ),
    ]
