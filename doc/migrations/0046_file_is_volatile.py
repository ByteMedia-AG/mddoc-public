# Generated by Django 5.2.4 on 2025-07-20 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0045_doc_completed_at_alter_doc_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='is_volatile',
            field=models.BooleanField(db_default=False, default=False),
        ),
    ]
