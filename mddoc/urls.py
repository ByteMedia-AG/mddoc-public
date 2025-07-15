"""
URL configuration for mddoc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from doc import views

urlpatterns = [
                  path('accounts/', include('django.contrib.auth.urls')),
                  # path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
                  path('admin/', admin.site.urls),
                  path("", views.docs, name="docs"),
                  path("doc/add/", views.doc_add, name="doc-add"),
                  path("doc/<int:id>/", views.doc, name="doc-detail"),
                  path("doc/<int:id>/edit/", views.doc_edit, name="doc-edit"),
                  path("doc/<int:id>/delete/", views.doc_delete, name="doc-delete"),
                  path("doc/<int:id>/restore/", views.doc_restore, name="doc-restore"),
                  path("doc/<int:id>/extract/", views.doc_extract, name="doc-extract"),
                  path("doc/<int:id>/add_log/", views.doc_add_log, name="doc-add-log"),
                  path("doc/<int:id>/flag/", views.doc_toggle_flag, name="doc-toggle-flag"),
                  path("doc/<int:id>/archive/", views.doc_toggle_archive, name="doc-toggle-archive"),
                  path("doc/<int:doc_id>/add_time/", views.time_add, name="doc-time-add"),
                  path("doc/tr/analyse/selection/", views.time_analyse_selection, name="doc-tr-analyse-selection"),
                  path("doc/tr/analyse/preview", views.time_analyse_preview, name="doc-tr-analyse-preview"),
                  path("doc/tr/analyse/download", views.time_analyse_download, name="doc-tr-analyse-download"),
                  path("doc/tr/set/settled", views.time_records_set_settled, name="doc-tr-set-settled"),
                  path("doc/tr/set/deleted", views.time_records_set_deleted, name="doc-tr-set-deleted"),
                  path("doc/database/cleanup", views.cleanup_database, name="doc-cleanup-database"),
                  path("doc/database/dump", views.dump_database, name="doc-dump-database"),
                  path("doc/status/", views.status, name="doc-status"),
                  path("doc/update/bulk", views.bulk_update, name="doc-bulk-update"),
                  path("doc/add/short", views.doc_add_short, name="doc-add-short"),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
