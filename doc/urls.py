# doc/urls.py
from django.urls import path

from . import views

app_name = 'doc'

urlpatterns = [
    path("", views.docs, name="home"),
    path("add/", views.doc_add, name="add"),
    path("<int:id>/", views.doc, name="detail"),
    path("<int:id>/pdf", views.create_pdf, name="create-pdf"),
    path("<int:id>/edit/", views.doc_edit, name="edit"),
    path("<int:id>/make/version/", views.doc_make_version, name="make-version"),
    path("<int:id>/delete/", views.doc_delete, name="delete"),
    path("<int:id>/restore/", views.doc_restore, name="restore"),
    path("<int:id>/extract/", views.doc_extract, name="extract"),
    path("<int:id>/add_log/", views.doc_add_log, name="add-log"),
    path("<int:id>/flag/", views.doc_toggle_flag, name="toggle-flag"),
    path("<int:id>/react_time/", views.doc_set_reactivation_time, name="set-react-time"),
    path("<int:id>/deadline/", views.doc_set_deadline, name="set-deadline"),
    path("<int:id>/archive/", views.doc_toggle_archive, name="toggle-archive"),
    path("<int:id>/checklist/", views.edit_checklist, name="edit-checklist"),
    path("<int:id>/checkitem/", views.check_checklist, name="check-item"),
    path("<int:id>/complete/", views.doc_toggle_completed, name="toggle-complete"),
    path("tr/analyse/selection/", views.time_analyse_selection, name="tr-analyse-selection"),
    path("tr/analyse/preview", views.time_analyse_preview, name="tr-analyse-preview"),
    path("tr/analyse/download", views.time_analyse_download, name="tr-analyse-download"),
    path("tr/set/settled", views.time_records_set_settled, name="tr-set-settled"),
    path("tr/set/deleted", views.time_records_set_deleted, name="tr-set-deleted"),
    path("database/cleanup", views.cleanup_database, name="cleanup-database"),
    path("filesystem/cleanup", views.cleanup_filesystem, name="cleanup-filesystem"),
    path("database/dump", views.dump_database, name="dump-database"),
    path("status/", views.status, name="status"),
    path("update/bulk", views.bulk_update, name="bulk-update"),
    path("add/short", views.doc_add_short, name="add-short"),
    path("<int:doc_id>/add_time/", views.time_add, name="time-add"),
    path("tags/suggest/", views.suggest_tags, name="tag-suggest"),
]
