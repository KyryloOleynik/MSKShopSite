# Generated by Django 5.1.6 on 2025-02-24 11:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SmartZamovApp', '0006_alter_customuser_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('active', 'Active'), ('shipped', 'Shipped'), ('canceled', 'Canceled')], default='pending', max_length=40),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_order', to='SmartZamovApp.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
