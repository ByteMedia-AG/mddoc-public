# Generated by Django 5.2.3 on 2025-06-20 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0007_alter_documentation_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentation',
            name='is_archived',
            field=models.BooleanField(default=False, verbose_name='Is considered archived'),
        ),
        migrations.AddField(
            model_name='documentation',
            name='is_markdown',
            field=models.BooleanField(default=True, verbose_name='Content uses Markdown'),
        ),
        migrations.AddField(
            model_name='documentation',
            name='uri',
            field=models.CharField(blank=True, max_length=2000, null=True, verbose_name='URI'),
        ),
        migrations.AlterField(
            model_name='documentation',
            name='text',
            field=models.TextField(null=True, verbose_name='Content'),
        ),
    ]
