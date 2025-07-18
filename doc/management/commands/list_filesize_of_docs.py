from django.core.management.base import BaseCommand

from doc.models import Doc


class Command(BaseCommand):
    help = "List the file size of docs."

    def handle(self, *args, **options):
        """"""

        for doc in Doc.objects.prefetch_related('files').filter(deleted_at__isnull=True, successor__isnull=False):
            file_count = doc.files.count()
            if file_count > 0:
                total_size = sum(f.file.size for f in doc.files.all())
                mb = float(total_size) / (1024 * 1024)
                if mb > 1:
                    print(f"Doc ID: {doc.id}, File Count: {file_count}, Total Size: {mb:.1f} MB")
