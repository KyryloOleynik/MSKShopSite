# Generated by Django 5.1.6 on 2025-02-25 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SmartZamovApp', '0009_message_is_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='patronymic',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
