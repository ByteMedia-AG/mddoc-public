from pathlib import Path

from django.db import migrations


def forwards(apps, schema_editor):
    Doc = apps.get_model('doc', 'Doc')
    FileModel = apps.get_model('doc', 'File')

    for doc in Doc.objects.exclude(file='').exclude(file__isnull=True):
        file_instance = FileModel.objects.create(
            file=doc.file,
            name=Path(doc.file.name).name,
        )
        doc.files.add(file_instance)


class Migration(migrations.Migration):
    dependencies = [
        ('doc', '0040_file_extension_file_mime_type_file_sha256_file_size_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
