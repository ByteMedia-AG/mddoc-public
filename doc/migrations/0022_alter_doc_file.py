# Generated by Django 5.2.3 on 2025-06-24 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0021_doc_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doc',
            name='file',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to='', verbose_name='File'),
        ),
    ]
