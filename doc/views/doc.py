import datetime
import difflib
import re

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.db import connection
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.db.models.functions import Lower
from django.db.utils import OperationalError
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import localtime
from django.utils.timezone import make_aware
from django.utils.timezone import now
from taggit.models import Tag

from doc.forms import ChecklistItemFormSet
from doc.forms import DocForm, TimeRecordForm
from doc.markdown import md2html
from doc.models import Doc
from doc.models import File
from doc.utils import extract_selected_info_from_url, get_tags_grouped, reactivate_docs, calculate_delta_time


@login_required
@permission_required("doc.search")
def docs(request):
    """List of documents."""

    reactivate_docs()

    tags = None
    error = False
    num_matches = 0

    if request.GET:
        params = request.GET.dict()
        request.session['docs_params'] = params
    else:
        params = request.session.get('docs_params', {})

    asc = bool(int(params.get('asc', 0)))
    oby = params.get('orderby', 'created')
    oby2 = oby
    if oby == 'updated':
        oby = 'updated_at'
    elif oby == 'title':
        oby = 'title'
    elif oby == 'time':
        oby = 'time'
    elif oby == 'deadline':
        oby = 'deadline'
    elif oby == 'created':
        oby = 'created_at'
    else:
        oby = 'updated_at'
    if not asc:
        oby = f'-{oby}'

    search_string = params.get('search', False)
    try:
        if search_string:
            entities = Doc.objects.match(search_string)
        else:
            entities = Doc.objects.all()
        if not params.get('ipr', False):
            # Do not include previous revisions.
            entities = entities.exclude(successor__isnull=False)
        if not params.get('idr', False):
            # Do not include deleted resources.
            entities = entities.exclude(successor__isnull=True, deleted_at__isnull=False)
        if not params.get('iar', False):
            # Do not include archived resources.
            entities = entities.exclude(is_archived=True)
        if params.get('flg', False):
            entities = entities.filter(is_flagged=True)
        if params.get('ddl', False):
            entities = entities.filter(deadline__isnull=False)
            # Entries whose deadline has passed and which have also been
            # marked as completed must be excluded.
            entities = entities.exclude(deadline__lte=now(), completed_at__isnull=False)
        if params.get('ustr', False):
            entities = entities.filter(has_unsettled_tr=True)
        if params.get('cgte', False):
            entities = entities.filter(created_at__gte=timezone.make_aware(parse_datetime(params.get('cgte'))))
        if params.get('clte', False):
            entities = entities.filter(created_at__lte=timezone.make_aware(parse_datetime(params.get('clte'))))
        if params.get('ugte', False):
            entities = entities.filter(updated_at__gte=timezone.make_aware(parse_datetime(params.get('ugte'))))
        if params.get('ulte', False):
            entities = entities.filter(updated_at__lte=timezone.make_aware(parse_datetime(params.get('ulte'))))
        if params.get('tgte', False):
            entities = entities.filter(time__gte=timezone.make_aware(parse_datetime(params.get('tgte'))))
        if params.get('tlte', False):
            entities = entities.filter(time__lte=timezone.make_aware(parse_datetime(params.get('tlte'))))
        num_matches = entities.count()

        if oby2 == 'deadline' or params.get('ddl', False):
            # When filtering for entries with a deadline, the deadline is
            # automatically set as the sorting criterion.
            if not params.get('ddl', False):
                # If you want to sort by deadline but do not want to restrict the
                # sorting to entries with a deadline, you must set a default value
                # for entries without a deadline.
                fallback_deadline = make_aware(datetime.datetime(1900, 1, 1))
                entities = entities.annotate(
                    sort_deadline=Coalesce('deadline', Value(fallback_deadline))
                ).order_by('sort_deadline' if asc else '-sort_deadline')[:100]
            else:
                # As only entries with a deadline can appear in the result set,
                # no default value is required at this point.
                # In addition, descending becomes ascending and vice versa, because
                # the interpretation of the deadline is different.
                entities = entities.order_by('-deadline' if asc else 'deadline')[:100]
        else:
            entities = entities.order_by(oby)[:100]

        entity_ids = [e.id for e in entities]
        available_tags = Doc.tags \
                             .most_common(extra_filters={'doc__in': entity_ids}) \
                             .filter(num_times__lt=len(entity_ids), num_times__gt=0) \
                             .order_by('-num_times', 'name')[:1000]
        if search_string:
            tags = [tag for tag in available_tags if tag.name.lower() not in search_string.lower()]
        else:
            tags = [tag for tag in available_tags]
    except OperationalError as oe:
        entities = Doc.objects.filter(deleted_at__isnull=True, is_archived=False).order_by('-id')[:10]
        error = oe
        print(oe)
    except Exception as e:
        print(e.__traceback__)

    if False:
        print("===================================")
        for query in connection.queries:
            time = float(query['time'])
            print(f"{time}  s: {query['sql']}")
            print("--------------------------------")

    return TemplateResponse(request, "docs.html", {
        'page_title': 'Search Resources',
        'entities': entities,
        'tags': get_tags_grouped(tags),
        'error': error,
        'asc': asc,
        'oby': oby2,
        'params': params,
        'num_matches': num_matches,
        'now': now(),
    })


@login_required
@permission_required("doc.bulk_update")
def bulk_update(request, **kwargs):
    """
    Allows to add/remove is_flagged, is_archived and tags.
    """

    success = []
    error = []

    show_exclusion_deleted_info = False
    show_initial_warning = False
    no_docs_left = False
    show_delete_warning = False

    if request.method == 'GET':
        doc_list = request.GET.getlist('doc') or []
        if len(doc_list) < 1:
            return HttpResponseRedirect(reverse("doc:home"))
        docs = Doc.objects.filter(
            successor__isnull=True,
            id__in=doc_list,
        ).order_by(Lower('title'))
        show_initial_warning = True
        if len(request.GET.getlist('doc') or []) > docs.count():
            show_exclusion_deleted_info = True

    if request.method == 'POST':
        docs = Doc.objects.filter(
            successor__isnull=True,
            id__in=request.POST.getlist('doc') or [],
        ).order_by(Lower('title'))

    if docs.count() < 1:
        no_docs_left = True

    if request.method == 'POST':
        try:
            for doc in docs:
                if request.POST.get('set-flag'):
                    doc.is_flagged = True
                    success.append(f'Doc {doc.id} is flagged.')
                if request.POST.get('unset-flag'):
                    doc.is_flagged = False
                    success.append(f'Doc {doc.id} is not flagged.')
                if request.POST.get('set-archived'):
                    doc.is_archived = True
                    doc.deleted_at = None
                    show_delete_warning = True
                    success.append(f'Doc {doc.id} is archived.')
                if request.POST.get('unset-archived'):
                    doc.is_archived = False
                    success.append(f'Doc {doc.id} is not archived.')
                if request.POST.get('set-deleted'):
                    doc.deleted_at = timezone.now()
                    doc.is_archived = False
                    show_delete_warning = True
                    success.append(f'Doc {doc.id} is marked as deleted.')
                if request.POST.get('unset-deleted'):
                    doc.deleted_at = None
                    success.append(f'Doc {doc.id} is not marked as deleted.')
                if request.POST.get('rm-tag'):
                    try:
                        tag = Tag.objects.get(id=request.POST.get('rm-tag'))
                        doc.tags.remove(tag)
                        success.append(f'Doc {doc.id} no longer has the tag "{tag.name}".')
                    except Tag.DoesNotExist:
                        error.append(f"Tag with ID {request.POST.get('rm-tag')} does not exist.")
                if request.POST.get('add-tag'):
                    tag_string = request.POST.get('add-tag')
                    tag_list = [tag.strip() for tag in tag_string.split(',') if tag.strip()]
                    for tag in tag_list:
                        doc.tags.add(tag)
                    success.append(f'Doc {doc.id} now has the tags "{tag_list}".')
                doc.tag = " ".join(sorted(doc.tags.slugs()))
                doc.save()
        except Exception as e:
            success = []
            error.append(e)

    tags = Doc.tags.filter(doc__in=docs).distinct().order_by('name')

    return TemplateResponse(request, "bulk_update.html", {
        'page_title': f"Bulk update",
        'docs': docs,
        'tags': tags,
        'show_exclusion_deleted_info': show_exclusion_deleted_info,
        'show_initial_warning': show_initial_warning,
        'no_docs_left': no_docs_left,
        'success': success,
        'error': error,
        'show_delete_warning': show_delete_warning,
    })


@login_required
@permission_required("doc.add")
def doc_add_short(request, **kwargs):
    """
    Shorter path to add a document. Only the description and optionally one
    or more tags are presented in the modal form. Other necessary information
    is added automatically to the entry.
    """

    if request.method != 'POST':
        return HttpResponseRedirect(reverse("doc:home"))

    description = request.POST.get('description', '').strip()
    tags = request.POST.get('tags', '').strip()

    if not description:
        return HttpResponseRedirect(reverse("doc:home"))

    now = timezone.now()
    local_now = localtime(now)
    datetime_string = local_now.strftime("%Y-%m-%d %H:%M %Z")

    d: Doc = Doc()
    d.title = f'Log - {datetime_string}'
    d.description = description
    d.time = now
    d.is_markdown = False
    d.is_archived = True
    d.is_flagged = False
    d.save()

    tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    for tag in tag_list:
        d.tags.add(tag)
    d.tags.add('log-entry')
    d.tag = " ".join(list(d.tags.slugs()))
    d.save()

    return HttpResponseRedirect(reverse("doc:home"))


@login_required
@permission_required("doc.add")
def doc_add(request, **kwargs):
    """Add a new document"""

    if request.method == 'POST':
        form = DocForm(request.POST, request.FILES)
        if form.is_valid():
            entity = form.save()
            for uploaded_file in request.FILES.getlist("upload"):
                file_obj = File.objects.create(file=uploaded_file, name=uploaded_file.name)
                entity.files.add(file_obj)
            entity.tag = " ".join(list(entity.tags.slugs()))
            entity.save()
            return HttpResponseRedirect(reverse("doc:detail", args=(entity.id,)))
    else:
        form = DocForm()

    return TemplateResponse(request, "doc-edit.html", {
        'page_title': "Add new document",
        'form': form,
    })


@login_required
@permission_required("doc.extract")
def doc_extract(request, **kwargs):
    """Extracts the text of the given URI."""

    doc_id = kwargs.get('id')
    error = None

    try:
        entity = Doc.objects.get(pk=doc_id)
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    if not entity.uri:
        return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))

    extracted_data = extract_selected_info_from_url(entity.uri)

    title_url = (entity.uri[:50] + '...') if len(entity.uri) > 50 else entity.uri

    return TemplateResponse(request, "doc_extract_text.html", {
        'page_title': f"Extract {title_url}",
        'error': error,
        'data': extracted_data,
    })


@login_required
@permission_required("doc.delete")
def doc_delete(request, **kwargs):
    """Sets the attribute doc.deleted_at to now()."""

    doc_id = kwargs.get('id')

    if request.method != 'POST':
        # In case of a GET request, a redirect to the corresponding details view is done.
        return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))

    try:
        entity = Doc.objects.get(pk=doc_id)
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    if request.method == 'POST':
        entity.remove()
        return HttpResponseRedirect(reverse("doc:home"))


@login_required
@permission_required("doc.restore")
def doc_restore(request, **kwargs):
    """Either undeleted the document or copies the values of the select entry to the current representation."""

    doc_id = kwargs.get('id')

    if request.method != 'POST':
        # In case of a GET request, a redirect to the corresponding details view is done.
        return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))

    try:
        entity = Doc.objects.get(pk=doc_id)
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    if entity.successor:
        entity.restore_revision()
        return HttpResponseRedirect(reverse("doc:detail", args=(entity.successor.id,)))
    else:
        # The deleted attribute has to be set to None
        entity.deleted_at = None
        entity.save()
        return HttpResponseRedirect(reverse("doc:detail", args=(entity.id,)))


@login_required
@permission_required("doc.edit")
def doc_edit(request, **kwargs):
    """Edit a document"""

    doc_id = kwargs.get('id')

    try:
        entity = Doc.objects.get(pk=doc_id)
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    show_revision_warning = False
    if request.method == 'GET' and not entity.is_archived:
        show_revision_warning = True

    if request.method == 'POST':
        form = DocForm(request.POST, request.FILES, instance=entity)
        if form.is_valid():
            entity.make_revision()
            entity = form.save()
            for uploaded_file in request.FILES.getlist("upload"):
                file_obj = File.objects.create(file=uploaded_file, name=uploaded_file.name)
                entity.files.add(file_obj)
            entity.is_archived = False
            entity.tag = " ".join(list(entity.tags.slugs()))
            delete_ids = form.cleaned_data.get("delete_files", [])
            if delete_ids:
                entity.files.remove(*File.objects.filter(id__in=delete_ids))
            entity.save()
            return HttpResponseRedirect(reverse("doc:detail", args=(entity.id,)))
    else:
        form = DocForm(instance=entity)
    return TemplateResponse(request, "doc-edit.html", {
        'page_title': f"{entity.title}",
        'form': form,
        'show_revision_warning': show_revision_warning,
        'doc_id': doc_id,
    })


@login_required
@permission_required("doc.add_log")
def doc_add_log(request, **kwargs):
    """Adds a log entry."""

    doc_id = kwargs.get('id')

    log_entry = request.POST.get('log_entry', default='').strip()
    if log_entry != '':
        log_entry = BeautifulSoup(log_entry, features="html.parser").get_text()

    if request.method != 'POST' or log_entry == '':
        return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))

    try:
        entity = Doc.objects.get(pk=doc_id)
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    now = datetime.datetime.now().replace(microsecond=0).isoformat()
    if entity.log:
        log_entry = f"<!-- {now} -->\n{log_entry}\n{entity.log}"
    else:
        log_entry = f"<!-- {now} -->\n{log_entry}"
    entity.log = log_entry
    entity.save()

    return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))


@login_required
@permission_required("doc.archive")
def doc_toggle_archive(request, **kwargs):
    """Set is_archived to True if it was False and the other way around."""

    doc_id = kwargs.get('id')

    try:
        entity = Doc.objects.get(pk=doc_id)
        if entity.is_archived:
            entity.is_archived = False
        else:
            entity.is_archived = True
        entity.save()
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))


@login_required
@permission_required("doc.edit")
def doc_make_version(request, **kwargs):
    """"""

    doc_id = kwargs.get('id')

    try:
        entity = Doc.objects.get(pk=doc_id)
        archived = entity.is_archived
        entity.is_archived = True
        entity.save()
        entity.make_revision()
        entity.is_archived = archived
        entity.save()
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))


@login_required
@permission_required("doc.edit")
def doc_toggle_completed(request, **kwargs):
    """"""

    doc_id = kwargs.get('id')

    if request.method != 'POST':
        return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))

    try:
        entity = Doc.objects.get(pk=doc_id)
        if entity.completed_at:
            entity.completed_at = None
        else:
            entity.completed_at = now()
        entity.save()
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))


@login_required
@permission_required("doc.flag")
def doc_toggle_flag(request, **kwargs):
    """Set is_flagged to True if it was False and the other way around."""

    doc_id = kwargs.get('id')

    try:
        entity = Doc.objects.get(pk=doc_id)
        if entity.is_flagged:
            entity.is_flagged = False
        else:
            entity.is_flagged = True
        entity.save()
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))


@login_required
@permission_required("doc.reactivation")
def doc_set_reactivation_time(request, **kwargs):
    """"""

    doc_id = kwargs.get('id')

    if request.method != 'POST':
        return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))

    set_time = request.POST.get("set-time", "").strip()
    reactivation_time_str = request.POST.get("reactivation_time", "").strip()
    reactivation_time = calculate_delta_time(set_time, reactivation_time_str)

    try:
        entity = Doc.objects.get(pk=doc_id)
        entity.reactivation_time = reactivation_time
        if reactivation_time:
            entity.is_flagged = False
            # entity.is_archived = True
        entity.save()
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))


@login_required
@permission_required("doc.reactivation")
def doc_set_deadline(request, **kwargs):
    """"""

    doc_id = kwargs.get('id')

    if request.method != 'POST':
        return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))

    set_time = request.POST.get("set-time", "").strip()
    deadline_str = request.POST.get("deadline", "").strip()
    deadline = calculate_delta_time(set_time, deadline_str)

    try:
        entity = Doc.objects.get(pk=doc_id)
        entity.deadline = deadline
        entity.save()
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    return HttpResponseRedirect(reverse("doc:detail", args=(doc_id,)))


@login_required
@permission_required("doc.view")
def doc(request, **kwargs):
    """Gets the details of the requested document."""

    doc_id = kwargs.get('id')

    try:
        entity = Doc.objects.get(pk=doc_id)
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    html = ""
    if entity.is_markdown:
        html = md2html(entity.text)

    diff = None
    if entity.successor:
        diff = difflib.unified_diff(str(entity.text).splitlines(), str(entity.successor.text).splitlines())
        diff = '\n'.join(diff)

    log = None
    if entity.log:
        pattern = re.compile(r'<!--\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s*-->\s*')
        matches = list(pattern.finditer(entity.log))
        log = []
        for i, match in enumerate(matches):
            dt = datetime.datetime.fromisoformat(match.group(1))
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(entity.log)
            log.append((dt, entity.log[start:end].strip()))

    overdue = False
    if entity.deadline and entity.deadline < now():
        overdue = True

    checklist_formset = ChecklistItemFormSet(queryset=entity.checklist_items.order_by('position'))

    images = [
        f for f in entity.files.all()
        if f.name.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]

    return TemplateResponse(request, "doc.html", {
        'page_title': f"{entity.title}",
        'entity': entity,
        'doc_id': doc_id,
        'html': html,
        'tags': list(entity.tags.all().order_by('name')),
        'is_deleted': True if entity.deleted_at else False,
        'is_revised': True if entity.successor else False,
        'successor_id': entity.successor.id if entity.successor else None,
        'revisions': entity.predecessors.order_by('updated_at').reverse(),
        'diff': diff,
        'log': log,
        'files': entity.files.all().order_by(Lower('name')),
        'time_record_form': TimeRecordForm(),
        'time_records': list(entity.time_records.all().order_by('-date')) if entity.time_records.exists() else False,
        'now': now(),
        'overdue': overdue,
        'checklist_formset': checklist_formset,
        'checklist': list(entity.checklist_items.order_by('position')),
        'images': images,
        'can_md2pdf': settings.DOC_ALLOW_MD2PDF,
    })
