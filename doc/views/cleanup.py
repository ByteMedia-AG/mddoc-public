import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.files import File as DjangoFile
from django.db.models import Subquery
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from taggit.models import TaggedItem

from doc.forms import CleanupForm
from doc.models import Doc, TimeRecord
from doc.models import File


@login_required
@permission_required("doc.cleanup")
def cleanup_database(request, **kwargs):
    """Allows to clean up the database."""

    success = False
    error = False

    if request.method == 'GET':
        form = CleanupForm()

        return TemplateResponse(request, "cleanup.html", {
            'page_title': "Database cleanup",
            'form': form,
            'success': success,
            'error': error,
        })

    if not request.POST:
        return HttpResponseRedirect(reverse("doc:home"))

    form = CleanupForm(request.POST)
    if form.is_valid():
        do_commit = request.POST.get('do_commit', default=False)
        number_of_deleted_docs = 0
        number_of_deleted_revisions = 0
        number_of_deleted_archived_revisions = 0
        number_of_removed_volatile_files = 0
        number_of_deleted_tr = 0
        number_of_settled_tr = 0
        number_of_undeleted_tr = 0
        number_of_unsettled_tr = 0
        number_of_removed_tags = 0
        if request.POST.get('remove_deleted_docs', default=False):
            deleted_docs = Doc.objects.filter(deleted_at__isnull=False, successor__isnull=True)
            if form.cleaned_data['from_date']:
                deleted_docs = deleted_docs.filter(created_at__gte=form.cleaned_data['from_date'])
            if form.cleaned_data['to_date']:
                deleted_docs = deleted_docs.filter(created_at__lte=form.cleaned_data['to_date'])
            number_of_deleted_docs = deleted_docs.count()
            if do_commit:
                for d in deleted_docs:
                    d.delete()
        if request.POST.get('remove_previous_revisions', default=False):
            revisions = Doc.objects.filter(deleted_at__isnull=False, successor__isnull=False)
            if form.cleaned_data['from_date']:
                revisions = revisions.filter(created_at__gte=form.cleaned_data['from_date'])
            if form.cleaned_data['to_date']:
                revisions = revisions.filter(created_at__lte=form.cleaned_data['to_date'])
            number_of_deleted_revisions = revisions.count()
            if do_commit:
                for d in revisions:
                    d.delete()
        if request.POST.get('remove_archived_revisions', default=False):
            archived_revisions = Doc.objects.filter(deleted_at__isnull=False, successor__is_archived=True)
            if form.cleaned_data['from_date']:
                archived_revisions = archived_revisions.filter(created_at__gte=form.cleaned_data['from_date'])
            if form.cleaned_data['to_date']:
                archived_revisions = archived_revisions.filter(created_at__lte=form.cleaned_data['to_date'])
            number_of_deleted_archived_revisions = archived_revisions.count()
            if do_commit:
                for d in archived_revisions:
                    d.delete()
        if request.POST.get('remove_unused_tags', default=False):
            doc_ct = ContentType.objects.get_for_model(Doc)
            live_doc_ids = Subquery(Doc.objects.values('id'))
            orphaned_tagged_items = TaggedItem.objects.filter(
                content_type=doc_ct
            ).exclude(object_id__in=live_doc_ids)
            number_of_removed_tags = orphaned_tagged_items.count()
            if do_commit:
                orphaned_tagged_items.delete()
        if request.POST.get('remove_deleted_timerecords', default=False):
            deleted_tr = TimeRecord.objects.filter(deleted_at__isnull=False)
            if form.cleaned_data['from_date']:
                deleted_tr = deleted_tr.filter(created_at__gte=form.cleaned_data['from_date'])
            if form.cleaned_data['to_date']:
                deleted_tr = deleted_tr.filter(created_at__lte=form.cleaned_data['to_date'])
            number_of_deleted_tr = deleted_tr.count()
            if do_commit:
                for d in deleted_tr:
                    d.delete()
        if request.POST.get('remove_settled_timerecords', default=False):
            settled_tr = TimeRecord.objects.filter(settled_at__isnull=False)
            if form.cleaned_data['from_date']:
                settled_tr = settled_tr.filter(created_at__gte=form.cleaned_data['from_date'])
            if form.cleaned_data['to_date']:
                settled_tr = settled_tr.filter(created_at__lte=form.cleaned_data['to_date'])
            number_of_settled_tr = settled_tr.count()
            if do_commit:
                for d in settled_tr:
                    d.delete()
        if request.POST.get('undo_delete_timerecords', default=False):
            restore_tr = TimeRecord.objects.filter(deleted_at__isnull=False)
            if form.cleaned_data['from_date']:
                restore_tr = restore_tr.filter(created_at__gte=form.cleaned_data['from_date'])
            if form.cleaned_data['to_date']:
                restore_tr = restore_tr.filter(created_at__lte=form.cleaned_data['to_date'])
            number_of_undeleted_tr = restore_tr.count()
            if do_commit:
                for tr in restore_tr:
                    tr.deleted_at = None
                    tr.save()
                    tr.doc.save()
        if request.POST.get('undo_settle_timerecords', default=False):
            unsettle_tr = TimeRecord.objects.filter(settled_at__isnull=False)
            if form.cleaned_data['from_date']:
                unsettle_tr = unsettle_tr.filter(created_at__gte=form.cleaned_data['from_date'])
            if form.cleaned_data['to_date']:
                unsettle_tr = unsettle_tr.filter(created_at__lte=form.cleaned_data['to_date'])
            number_of_unsettled_tr = unsettle_tr.count()
            if do_commit:
                for tr in unsettle_tr:
                    tr.settled_at = None
                    tr.save()
                    tr.doc.save()
        success = [
            f'{number_of_deleted_docs} documents have been removed.',
            f'{number_of_deleted_revisions} revisions have been removed.',
            f'{number_of_deleted_archived_revisions} archived revisions have been removed.',
            f'{number_of_removed_volatile_files} volatile files have been removed.',
            f'{number_of_removed_tags} tags have been removed.',
            f'{number_of_deleted_tr} time records marked as deleted have been removed.',
            f'{number_of_settled_tr} time records marked as settled have been removed.',
            f'{number_of_undeleted_tr} time records marked as deleted have been restored.',
            f'{number_of_unsettled_tr} time records marked as settled have been restored.',
        ]

        context = {
            'page_title': "Database cleanup",
            'success': success,
            'error': error,
            'faked': True if not do_commit else False,
        }
        if not do_commit:
            context['form'] = form
        return TemplateResponse(request, "cleanup.html", context)
    else:
        return TemplateResponse(request, "cleanup.html", {
            'page_title': "Database cleanup",
            'form': form,
            'success': success,
            'error': error,
        })


@login_required
@permission_required("doc.cleanup")
def cleanup_filesystem(request, **kwargs):
    """Allows to clean up the media directory."""

    success = []
    error = []

    if request.method == 'POST':
        try:
            result = subprocess.run(
                [sys.executable, 'manage.py', 'cleanup_filesystem'],
                cwd=settings.BASE_DIR,
                check=True,
                capture_output=True,
                text=True,
            )
            output = result.stdout

            now = timezone.now()
            datetime_string = now.strftime("%Y-%m-%d %H:%M")
            doc = Doc.objects.create(
                title=f"Filesystem cleanup of {datetime_string}",
                text=output,
                is_markdown=False,
                is_archived=True,
                time=now,
                tag='syslog cleanup filesystem',
                description=f'This is an automatically created entry from the filesystem cleanup process.',
            )
            doc.tags.add("syslog")
            doc.tags.add("cleanup")
            doc.tags.add("filesystem")
            doc.save()

            success.append('The cleanup has been done.')
            success.append('The protocol of the process has been saved in the database.')
            success.append('A zip file with the removed files can be found in the directory named trash.')

        except subprocess.CalledProcessError as e:
            error.append("The cleanup command failed.")
            error.append(f"Error output:\n{e.stderr}")

    return TemplateResponse(request, "cleanup_filesystem.html", {
        'page_title': "Cleanup filesystem",
        'success': success,
        'error': error,
    })


@login_required
@permission_required("doc.dump_database")
def dump_database(request, **kwargs):
    """Does a dump of the database."""

    success = []
    error = []

    if request.method == 'POST':
        save_as_doc = request.POST.get('target_rmdoc', default=False)
        save_as_file = request.POST.get('target_filesystem', default=False)
        if not save_as_doc and not save_as_file:
            error.append('No storage location has been selected.')
        else:
            try:
                timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"sqlite_backup_{timestamp}.sql"
                db_path = settings.DATABASES['default']['NAME']

                if save_as_file and not save_as_doc:
                    backup_dir = os.path.join(settings.BASE_DIR, 'db_dumps')
                    os.makedirs(backup_dir, exist_ok=True)
                    backup_path = os.path.join(backup_dir, backup_filename)
                    with open(backup_path, 'w') as f:
                        subprocess.run(['sqlite3', db_path, '.dump'], check=True, stdout=f)
                    success.append(f"The database dump has been saved to: {backup_path}")
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".sql") as tmp:
                        subprocess.run(['sqlite3', db_path, '.dump'], check=True, stdout=tmp)
                        tmp_path = tmp.name
                    # Create a Doc entry
                    with open(tmp_path, 'rb') as f:
                        now = timezone.now()
                        datetime_string = now.strftime("%Y-%m-%d %H:%M")
                        date_string = now.strftime("%Y-%m-%d")
                        doc = Doc.objects.create(
                            title=f"Database Backup {date_string}",
                            is_markdown=False,
                            is_archived=True,
                            time=now,
                            tag='db-dump',
                            description=f'This is an automatically created entry from a database backup. The dump was created {datetime_string}.',
                        )
                        doc.tags.add("db-dump")
                        django_file = DjangoFile(f)
                        django_file.name = Path(backup_filename).name
                        file_obj = File.objects.create(
                            file=django_file,
                            name=Path(backup_filename).name
                        )
                        doc.files.add(file_obj)
                        doc.save()
                        success.append(f"The database dump has been saved as document: {doc.title}")
                    if save_as_file:
                        # Move the file to the dir db_dumps
                        backup_dir = os.path.join(settings.BASE_DIR, 'db_dumps')
                        os.makedirs(backup_dir, exist_ok=True)
                        backup_path = os.path.join(backup_dir, backup_filename)
                        shutil.copy(tmp_path, backup_path)
                        success.append(f"The database dump has been saved to: {backup_path}")
                    os.remove(tmp_path)
            except Exception as e:
                traceback.print_exc()
                error.append(f"An exception occurred: {e}")

    return TemplateResponse(request, "database_dump.html", {
        'page_title': "Database dump",
        'success': success,
        'error': error,
    })
