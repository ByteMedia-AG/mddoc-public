from django.db.models import Count

from doc.models import File


def duplicate_files():
    """
    Returns a list of sets, where each set contains two file objects:
    (file to be deleted, file to be kept). The oldest file (after uploaded_at)
    is kept in each case.
    """
    duplicates = []

    duplicate_groups = (
        File.objects
        .values('name', 'sha256')
        .annotate(dupes=Count('id'))
        .filter(dupes__gt=1)
    )

    for group in duplicate_groups:
        dupes = list(File.objects.filter(name=group['name'], sha256=group['sha256']).order_by('uploaded_at'))
        keeper = dupes[0]
        for f in dupes[1:]:
            duplicates.append((f, keeper))

    return duplicates
