from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Min, Max, F, Sum
from django.template.response import TemplateResponse

from doc.models import Doc, TimeRecord
from doc.models import File
from doc.utils import flatten_settings, duplicate_files


@login_required
@permission_required("doc.show_status")
def status(request, **kwargs):
    """Shows information about the data persisted."""

    docs = {}
    doc_time = {}
    trs = {}
    trs_time = {}
    file = {}
    file_time = {}

    docs['All'] = Doc.objects.all().count()
    docs['Current'] = Doc.objects.filter(
        deleted_at__isnull=True, successor__isnull=True).count()
    docs['Current, with unsettled time records'] = TimeRecord.objects.filter(
        settled_at__isnull=True, deleted_at__isnull=True,
        doc__deleted_at__isnull=True, doc__successor__isnull=True).values_list('doc_id', flat=True).distinct().count()
    docs['Current, with file attachment'] = Doc.objects.annotate(num_files=Count('files')).filter(
        deleted_at__isnull=True, successor__isnull=True, num_files__gt=0).count()
    docs['Archived'] = Doc.objects.filter(
        deleted_at__isnull=True, successor__isnull=True, is_archived=True).count()
    docs['Versions'] = Doc.objects.filter(
        deleted_at__isnull=True, successor__isnull=False).count()
    docs['Revisions'] = Doc.objects.filter(
        deleted_at__isnull=False, successor__isnull=False).count()
    docs['Deleted'] = Doc.objects.filter(
        deleted_at__isnull=False, successor__isnull=True).count()

    doc_time['Youngest'] = Doc.objects.aggregate(Max('created_at'))['created_at__max']
    doc_time['Oldest'] = Doc.objects.aggregate(Min('created_at'))['created_at__min']

    trs['All'] = TimeRecord.objects.all().count()
    trs['Unsettled'] = TimeRecord.objects.filter(
        settled_at__isnull=True, deleted_at__isnull=True, doc__deleted_at__isnull=True, doc__is_archived=False).count()
    trs['Settled'] = TimeRecord.objects.filter(
        settled_at__isnull=False
    ).count()
    trs['Deleted'] = TimeRecord.objects.filter(
        deleted_at__isnull=False
    ).count()

    file_time['Youngest'] = File.objects.aggregate(Max('uploaded_at'))['uploaded_at__max']
    file_time['Oldest'] = File.objects.aggregate(Min('uploaded_at'))['uploaded_at__min']

    file['All'] = File.objects.all().count()
    file['Duplicates'] = (
        File.objects
        .values('name', 'sha256')
        .annotate(dupes=Count('id'))
        .filter(dupes__gt=1)
        .aggregate(redundant=Sum(F('dupes') - 1))['redundant'] or 0
    )
    file['Orphaned'] = File.objects.filter(docs__isnull=True).count()

    # if True:
    #     duplicate_groups = (
    #         File.objects
    #         .values('name', 'sha256')
    #         .annotate(dupes=Count('id'))
    #         .filter(dupes__gt=1)
    #     )
    #     for group in duplicate_groups:
    #         dupes = File.objects.filter(name=group['name'], sha256=group['sha256'])
    #         print(f"\nDuplicate group: name={group['name']}, sha256={group['sha256']}")
    #         for f in dupes:
    #             print(f" - ID: {f.id}, path: {f.file.path}, created: {f.uploaded_at}")

    trs_time['Youngest'] = TimeRecord.objects.aggregate(Max('created_at'))['created_at__max']
    trs_time['Oldest'] = TimeRecord.objects.aggregate(Min('created_at'))['created_at__min']

    settings_dict = {
        k: getattr(settings, k)
        for k in dir(settings)
        if k.isupper()
    }
    flat_settings = flatten_settings(settings_dict)

    return TemplateResponse(request, "status.html", {
        'page_title': "Status",
        'docs': docs,
        'doc_time': doc_time,
        'trs': trs,
        'trs_time': trs_time,
        'file': file,
        'file_time': file_time,
        'settings': flat_settings,
    })
