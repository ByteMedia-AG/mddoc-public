from django.core.management.base import BaseCommand

from doc.md2pdf import create_pdf


class Command(BaseCommand):
    help = "Test of the md2pdf implementation"

    def handle(self, *args, **options):
        """"""

        # create_pdf(1484)
        # create_pdf(1559)
        create_pdf(799)
