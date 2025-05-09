# Generated by Django 5.1.6 on 2025-02-21 23:21

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SmartZamovApp', '0003_alter_product_image2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='description_de',
            field=ckeditor.fields.RichTextField(null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='description_ru',
            field=ckeditor.fields.RichTextField(null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='description_uk',
            field=ckeditor.fields.RichTextField(null=True),
        ),
    ]
