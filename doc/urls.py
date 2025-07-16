# doc/urls.py
from django.urls import path

from . import views

app_name = 'doc'

urlpatterns = [
    path("", views.docs, name="home"),
    path("add/", views.doc_add, name="add"),
    path("<int:id>/", views.doc, name="detail"),
    path("<int:id>/edit/", views.doc_edit, name="edit"),
    path("<int:id>/delete/", views.doc_delete, name="delete"),
    path("<int:id>/restore/", views.doc_restore, name="restore"),
    path("<int:id>/extract/", views.doc_extract, name="extract"),
    path("<int:id>/add_log/", views.doc_add_log, name="add-log"),
    path("<int:id>/flag/", views.doc_toggle_flag, name="toggle-flag"),
    path("<int:id>/archive/", views.doc_toggle_archive, name="toggle-archive"),
    path("tr/analyse/selection/", views.time_analyse_selection, name="tr-analyse-selection"),
    path("tr/analyse/preview", views.time_analyse_preview, name="tr-analyse-preview"),
    path("tr/analyse/download", views.time_analyse_download, name="tr-analyse-download"),
    path("tr/set/settled", views.time_records_set_settled, name="tr-set-settled"),
    path("tr/set/deleted", views.time_records_set_deleted, name="tr-set-deleted"),
    path("database/cleanup", views.cleanup_database, name="cleanup-database"),
    path("database/dump", views.dump_database, name="dump-database"),
    path("status/", views.status, name="status"),
    path("update/bulk", views.bulk_update, name="bulk-update"),
    path("add/short", views.doc_add_short, name="add-short"),
    path("<int:doc_id>/add_time/", views.time_add, name="time-add"),
]
