import datetime

from django.utils.timezone import now

from doc.models import Doc

_last_run = None


def reactivate_docs():
    """
    Sets documents whose reactivation time is in the past to active again
    (Doc.is_archived=False).
    """

    global _last_run
    interval = datetime.timedelta(minutes=5)

    if _last_run is not None and now() - _last_run < interval:
        return

    _last_run = now()

    due_docs = Doc.objects.filter(
        reactivation_time__isnull=False,
        reactivation_time__lte=now(),
        successor__isnull=True,
    )

    for doc in due_docs:
        doc.is_archived = False
        doc.is_flagged = True
        doc.reactivation_time = None
        doc.save()
