from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

from django.core.management.base import BaseCommand

from doc.models import File


class Command(BaseCommand):
    help = "Remove orphaned files from filesystem and database"

    def handle(self, *args, **options):
        trash_dir = Path("trash")
        trash_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        zip_path = trash_dir / f"orphaned_files-{timestamp}.zip"
        orphans = File.objects.filter(docs__isnull=True)
        with ZipFile(zip_path, "w") as zipf:
            for f in orphans:
                file_path = Path(f.file.path)
                if file_path.exists():
                    zipf.write(file_path, arcname=f.file.name)
                    file_path.unlink()
        orphans.delete()
