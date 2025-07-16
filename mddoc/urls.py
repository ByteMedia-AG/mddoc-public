from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from doc.views import docs

urlpatterns = [
                  path('', docs, name='home'),
                  path('accounts/', include('django.contrib.auth.urls')),
                  path('admin/', admin.site.urls),
                  path("doc/", include("doc.urls")),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
