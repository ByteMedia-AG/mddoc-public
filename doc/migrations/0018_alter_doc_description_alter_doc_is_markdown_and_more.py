# Generated by Django 5.2.3 on 2025-06-22 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0017_alter_doc_is_archived'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doc',
            name='description',
            field=models.TextField(blank=True, help_text='The description is displayed below the title in the search results.', max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='doc',
            name='is_markdown',
            field=models.BooleanField(default=True, help_text='If checked, the text will be rendered by a markdown parser.', verbose_name='Content uses Markdown'),
        ),
        migrations.AlterField(
            model_name='doc',
            name='time',
            field=models.DateTimeField(blank=True, db_index=True, help_text='For emails, logs or results data.', null=True, verbose_name='Associated point in time'),
        ),
        migrations.AlterField(
            model_name='doc',
            name='title',
            field=models.CharField(db_index=True, help_text='The title of the document (shown as headline in the search results view.)', max_length=128),
        ),
    ]
