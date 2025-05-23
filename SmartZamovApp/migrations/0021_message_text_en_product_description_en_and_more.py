# Generated by Django 5.1.6 on 2025-03-20 20:37

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SmartZamovApp', '0020_customuser_tg_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='text_en',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='description_en',
            field=ckeditor.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='name_en',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='price_en',
            field=models.DecimalField(decimal_places=2, max_digits=13, null=True),
        ),
        migrations.AddField(
            model_name='product_category',
            name='name_en',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
