# Generated by Django 4.2 on 2024-10-17 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0002_alter_tenant_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenant',
            name='logo',
            field=models.ImageField(upload_to='static/'),
        ),
    ]
