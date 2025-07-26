from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from doc.models import Doc
from taggit.models import Tag


@require_GET
@login_required
def suggest_tags(request):
    """"""

    q = request.GET.get("q", "").lower()

    used_tags = Tag.objects.filter(taggit_taggeditem_items__content_type__model='doc') \
                           .values_list("name", flat=True).distinct()

    matching = sorted(
        tag for tag in used_tags if q in tag.lower()
    )[:10]

    return JsonResponse(matching, safe=False)
