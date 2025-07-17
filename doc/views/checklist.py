from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from doc.forms import ChecklistItemFormSet
from doc.models import Doc, ChecklistItem


@login_required
@permission_required("doc.edit")
def check_checklist(request, **kwargs):
    """"""

    doc_id = kwargs.get('id')

    try:
        entity = Doc.objects.get(pk=doc_id)
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    if request.method == 'POST':
        for item in entity.checklist_items.all():
            key = f"check_{item.id}"
            item.checked = key in request.POST
            item.save()

    return HttpResponseRedirect(reverse("doc:detail", args=(entity.id,)))


@login_required
@permission_required("doc.edit")
def edit_checklist(request, **kwargs):
    """"""

    doc_id = kwargs.get('id')

    try:
        entity = Doc.objects.get(pk=doc_id)
    except Doc.DoesNotExist as e:
        return TemplateResponse(request, "doc.html", {
            'page_title': f"Documentation - ID {doc_id}",
            'doc_id': doc_id,
            'error': 404,
        })

    if request.method == 'POST':
        formset = ChecklistItemFormSet(request.POST)

        if formset.is_valid():
            existing_items = entity.checklist_items.all()
            form_items = formset.save(commit=False)
            submitted_ids = []

            for form in formset.forms:
                cleaned = form.cleaned_data
                item_id = cleaned.get('id')
                if isinstance(item_id, ChecklistItem):
                    item_id = item_id.id
                description = cleaned.get('description', '').strip()

                if item_id and not description:
                    ChecklistItem.objects.filter(id=item_id, doc=entity).delete()
                elif description:
                    item = form.save(commit=False)
                    item.doc = entity
                    item.save()
                    submitted_ids.append(item.id)

            for item in existing_items:
                if item.id not in submitted_ids and item.description.strip():
                    item.delete()

    return HttpResponseRedirect(reverse("doc:detail", args=(entity.id,)))
