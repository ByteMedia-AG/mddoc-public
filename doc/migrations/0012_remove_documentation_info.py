# Generated by Django 5.2.3 on 2025-06-21 10:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0011_documentation_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentation',
            name='info',
        ),
    ]
