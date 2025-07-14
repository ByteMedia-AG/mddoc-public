import re

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.utils import timezone
from taggit.managers import TaggableManager


class SearchManager(models.Manager):
    """"""

    def match(self, query):
        """
        Match uses the FTS5 extension of SQLite. On other databases the method must be updated accordingly.
        Additonally the virtual table as well as the triggers must be applied beforehand.
        ---
        /doc/management/commands/refresh_text_index.py
        ./manage.py refresh_text_index.py
        """

        def repl_tag(m):
            tag = m.group(1)
            if tag.endswith('*'):
                return f'tag:{tag}'
            return f'tag:"{tag}"'

        query = re.sub(r'\b(and|or|not|near)\b', lambda m: m.group(1).upper(), query, flags=re.IGNORECASE)
        query = re.sub(r'#(\S+)', repl_tag, query)
        query = re.sub(r'\s+', ' ', query).strip()  # Normalize the query string.

        qs = self.get_queryset()

        if query:
            # The test is necessary, because the query term might have vanished in the normalization process above.
            qs = qs.filter(id__in=RawSQL("SELECT id FROM doc_doc_idx WHERE doc_doc_idx MATCH %s", [query]))

        return qs

    def search(self, query):
        terms = query.split()
        qs = self
        for term in terms:
            qs = qs.filter(Q(title__contains=term))
        return qs.distinct()


class Doc(models.Model):
    """
    The model represents either a document (if URI is empty) or
    meta information about a resource that is referenced by the URI.
    """

    title = models.CharField(null=False, blank=False, max_length=128, db_index=True, help_text="The title of the document (shown as headline in the search results view.)")
    description = models.TextField(null=True, blank=True, max_length=400, help_text="The description is displayed below the title in the search results.")
    text = models.TextField(null=True, blank=True, verbose_name='Content')
    is_markdown = models.BooleanField(null=False, default=True, verbose_name='Content uses Markdown', help_text="If checked, the text will be rendered by a markdown parser.")
    is_archived = models.BooleanField(null=False, default=False, db_index=True, verbose_name='Is considered archived or stale', help_text="If checked, the document is initially excluded in the search view.")
    uri = models.CharField(null=True, blank=True, max_length=2000, verbose_name='URI', help_text='If a URI is labelled, then the resource is regarded as meta information for the resource referenced with the URI.')
    tags = TaggableManager(blank=True)
    tag = models.TextField(blank=True, null=True)  # Holds the string representation of the tags.
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    successor = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='predecessors')
    time = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name='Associated point in time', help_text='For emails, logs or results data.')
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True, db_index=True)
    file = models.FileField(blank=True, null=True, max_length=255, upload_to='doc/%Y/%m', verbose_name='File')
    log = models.TextField(blank=True, null=True, verbose_name='Log')  # Holds the log entries as a delimited string.
    is_flagged = models.BooleanField(null=False, blank=False, verbose_name="Is flagged", default=False, db_index=True)
    last_settlement = models.DateField(blank=True, null=True, db_index=True, verbose_name='Last settlement', help_text='Date of the last settlement of outstanding hours')
    has_unsettled_tr = models.BooleanField(null=False, default=False, verbose_name='Has unsettled time records')

    objects = SearchManager()

    def remove(self, using=None, keep_parents=False):
        """
        In contrast to the delete() method, remove() only sets the updated_at
        attribute to the current time. Entities whose successor is None and
        deleted_at is not None are regarded as deleted by the application logic.
        """
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def make_revision(self):
        """
        Makes a copy of the entity, flags the copy as deleted and adds a reference to the
        copy to the entity. A tuple that is flagged as deleted and pointing to the current
        entity is considered as a previous revision. A tuple that is not deleted, but
        pointing to the current entity is considered as a archived version.

        The copy inherits the 'tag' attribute, but not the tag relations. However, the
        tags remain in the index and are searchable.
        """
        revision = Doc.objects.get(pk=self.pk)
        revision.pk = None
        if revision.is_archived and revision.successor is None:
            revision.deleted_at = None
        else:
            revision.deleted_at = timezone.now()
        revision.successor = self
        revision.save()

    def restore_revision(self):
        """
        Restores a previous revision to be the current entity.

        If a previous revision is retrieved as the current entity,
        the relations to taggit and the 'tag' attribute remain unchanged
        in the parent element.The reason for this is that keywords (tags)
        added in the meantime would otherwise be lost in the current entry.
        """
        successor = self.successor
        successor.make_revision()
        successor.title = self.title
        successor.text = self.text
        successor.description = self.description
        successor.is_markdown = self.is_markdown
        successor.is_archived = self.is_archived
        successor.uri = self.uri
        successor.file = self.file
        successor.time = self.time
        successor.deleted_at = None
        successor.save()

    def delete(self, *args, **kwargs):
        """"""

        for predecessor in self.predecessors.all():
            predecessor.delete()
        self.time_records.all().delete()
        super().delete(*args, **kwargs)

    def save(self, *args, update_unsettled_tr=True, **kwargs):
        if self.pk:
            self.has_unsettled_tr = self.time_records.filter(settled_at__isnull=True, deleted_at__isnull=True).exists()
        if not self.time:
            self.time = self.created_at or timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("search", "Can search documents"),
            ("add_time_record", "Can add time records"),
            ("time_analyse", "Can analyse time records"),
            ("extract", "Can extract text from uri of documents"),
            ("restore", "Can restore deleted documents"),
            ("edit", "Can edit documents"),
            ("add_log", "Can add logs to documents"),
            ("flag", "Can flag documents"),
            ("view", "Can view documents"),
        ]


class TimeRecord(models.Model):
    """
    The model represents a time record with a relation to a document it belongs to.
    """

    doc = models.ForeignKey(Doc, null=False, blank=False, on_delete=models.CASCADE, related_name='time_records')
    user = models.ForeignKey(get_user_model(), null=False, blank=False, on_delete=models.RESTRICT, related_name='time_records', verbose_name='User')
    time = models.FloatField(verbose_name='Hours', blank=False, null=False)
    date = models.DateField(null=False, blank=True, verbose_name='Date', db_index=True)
    description = models.CharField(null=True, blank=False, max_length=255, verbose_name='Description')
    settled_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)


class ChecklistItem(models.Model):
    """
    The model holds the checklist items.
    """

    doc = models.ForeignKey(Doc, null=False, blank=False, on_delete=models.CASCADE, related_name='checklist_items')
    description = models.CharField(null=False, blank=False, max_length=255, verbose_name='Item description')
    position = models.PositiveIntegerField(null=True, blank=True)
