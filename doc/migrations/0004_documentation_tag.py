# Generated by Django 5.2.3 on 2025-06-19 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0003_remove_documentation_tokens'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentation',
            name='tag',
            field=models.TextField(blank=True, null=True),
        ),
    ]
